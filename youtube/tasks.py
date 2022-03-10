from celery_progress.backend import ProgressRecorder
from celery import shared_task
from .models import VideoInfo
from accounts.models import User
import yt_dlp
import time
from datetime import datetime, timedelta
import os
import json
from hurry.filesize import size
import requests
from django.utils import timezone
from django.conf import settings
import redis
import ffmpeg


redis_instance = redis.StrictRedis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, charset="utf-8", decode_responses=True,)

use_proxy = True


@shared_task()
def extract_video_info(url_key):
    if use_proxy:
        ydl_opts = {
            "proxy": "socks5://127.0.0.1:7890",
        }
    else:
        ydl_opts = {}
    url = str(redis_instance.hgetall(url_key)["url"])
    user_email = redis_instance.hgetall(url_key)["user_email"]
    video_id_str = ""
    if "&list=" in url or "list=" in url:
        playlist_url = url
        # extract playlist of videos url
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(playlist_url, download=False)
            # f = open('info_playlist.json', 'a+')
            # json.dump(video_info, f)
            # f.close()
            playlist_id = video_info["id"]
            playlist_dir = f'{playlist_id}/'
            base_path = os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))+'/media/'+f'{user_email}/'
            playlist_path = base_path+playlist_dir
            os.makedirs(playlist_path, exist_ok=True)
            redis_instance.hmset(url_key, {'playlist_id': playlist_id})
            for single_video in video_info["entries"]:
                videofile_path = playlist_path+single_video["id"]
                os.makedirs(videofile_path, exist_ok=True)
                video_url = f'https://www.youtube.com/watch?v={single_video["id"]}'
                for imginfo in single_video["thumbnails"]:
                    if "hqdefault.jpg" in imginfo["url"]:
                        url = imginfo["url"]
                        if use_proxy:
                            proxies = {
                                "http": "socks5h://127.0.0.1:7890",
                                "https": "socks5h://127.0.0.1:7890",
                            }
                            res = requests.get(
                                url, allow_redirects=True, proxies=proxies)
                        else:
                            res = requests.get(url, allow_redirects=True)
                        open(f'{videofile_path}/{single_video["id"]}.jpg', 'wb+').write(res.content)
                        img_url = f'/media/{user_email}/{playlist_id}/{single_video["id"]}/{single_video["id"]}.jpg'

                formats = single_video.get("formats", [single_video])
                # if f["format_id"] in ["160", "133", "18"]:
                for f_note in single_video["formats"]:
                    
                    if f_note["format_note"] == "medium":
                        audio_url = f_note["url"]
                        # if not os.path.exists(videofile_path + f'/{single_video["id"]}'):
                        #     if use_proxy:
                        #         ydl_opts = {
                        #             "proxy": "socks5://127.0.0.1:7890",
                        #             "outtmpl": videofile_path + f'/{single_video["id"]}.mp3',
                        #         }
                        #     else:
                        #         ydl_opts = {
                        #             "outtmpl": videofile_path + f'/{single_video["id"]}.mp3',
                        #         }
                        #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        #         ydl.extract_info(audio_url)
                # get all resolution of mp4 format
                list_format = []
                for f in formats:
                    if f["ext"] == "mp4" and f["format_id"] in ["160", "133", "18", "135", "22", "137", "271", "313", ]:
                        tmp_info_list = []
                        tmp_info_list.append(f["format_id"])
                        tmp_info_list.append(f["format_note"])
                        if f["filesize"] != None:
                            filesize = size(int(f["filesize"]))
                        elif f["filesize"] == None:
                            video_file_url = f["url"]
                            if use_proxy:
                                proxies = {
                                    "http": "socks5h://127.0.0.1:7890",
                                    "https": "socks5h://127.0.0.1:7890",
                                }
                                filesize = size(int(requests.head(video_file_url, proxies=proxies).headers.get("content-length", 0)))
                            else:
                                filesize = size(int(requests.head(video_file_url).headers.get("content-length", 0)))
                        tmp_info_list.append(filesize)
                        list_format.append(tmp_info_list)

                VideoInfo.objects.get_or_create(
                    video_url=video_url,
                    playlist_id=playlist_id,
                    playlist_url=playlist_url,
                    is_playlist=True,
                    video_id=single_video["id"],
                    video_title=single_video["title"],
                    video_thumb_url=img_url,
                    video_formats=list_format,
                )
                video_id_str += f'{single_video["id"]},'
        redis_instance.hmset(url_key, {"videos_id": video_id_str})

    # extract single video url
    elif "?v=" in url and "&list=" not in url:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(url, download=False)
            # f = open('info_singlevideo.json', 'a+')
            # json.dump(video_info, f)
            # f.close()
            redis_instance.hmset(url_key, {"video_id": video_info["id"]})
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/media/'+f'{user_email}/'
            video_id_path = f'{video_info["id"]}/'
            single_video_dir = base_path+video_id_path
            os.makedirs(single_video_dir, exist_ok=True)
            # get image url
            for imginfo in video_info["thumbnails"]:
                if "hqdefault.jpg" in imginfo["url"]:
                    url = imginfo["url"]
                    if use_proxy:
                        proxies = {
                            "http": "socks5h://127.0.0.1:7890",
                            "https": "socks5h://127.0.0.1:7890",
                        }
                        res = requests.get(url, allow_redirects=True, proxies=proxies)
                    else:
                        res = requests.get(url, allow_redirects=True)
                    open(f'{single_video_dir}/{video_info["id"]}.jpg', 'wb+').write(res.content)
                    img_url = f'/media/{user_email}/{video_info["id"]}/{video_info["id"]}.jpg'

            # get all resolution of mp4 format
            formats = video_info.get("formats", [video_info])
            list_format = []
            for f in formats:
                if f["ext"] == "mp4" and f["format_id"] in ["160", "133", "18", "135", "22", "137", "271", "313", ]:
                    tmp_info_list = []
                    tmp_info_list.append(f["format_id"])
                    tmp_info_list.append(f["format_note"])
                    if f["filesize"] != None:
                        filesize = size(int(f["filesize"]))
                    elif f["filesize"] == None:
                        video_file_url = f["url"]
                        if use_proxy:
                            proxies = {
                                "http": "socks5h://127.0.0.1:7890",
                                "https": "socks5h://127.0.0.1:7890",
                            }
                            filesize = size(int(requests.head(video_file_url, proxies=proxies).headers.get("content-length", 0)))
                        else:
                            filesize = size(int(requests.head(video_file_url).headers.get("content-length", 0)))
                    tmp_info_list.append(filesize)
                    list_format.append(tmp_info_list)
            VideoInfo.objects.create(
                video_url=url,
                video_id=video_info["id"],
                video_title=video_info["title"],
                video_thumb_url=img_url,
                video_formats=list_format,
            )

    return "success"

##
# Start single video downloading process
##

def ffmpeg_concat(format_note, video_id, user_email):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    noaudio_filename = f"n{video_id}-{format_note}.mp4"
    noaudio_filepath = base_dir + f"/media/{user_email}/{video_id}/" + noaudio_filename
    audio_path = base_dir + f"/media/{user_email}/{video_id}/" + f"{video_id}.mp3"
    ffmpeg_input_video = ffmpeg.input(noaudio_filepath)
    ffmpeg_input_audio = ffmpeg.input(audio_path)
    ffmpeg.concat(ffmpeg_input_video, ffmpeg_input_audio, v=1, a=1).output(
                base_dir + f"/media/{user_email}/{video_id}/{video_id}-{format_note}.mp4").run(overwrite_output=True)
    after_concat_filename = f"{video_id}-{format_note}.mp4"
    after_concat_filepath = base_dir + f"/media/{user_email}/{video_id}/" + after_concat_filename
    os.remove(noaudio_filepath)
    return after_concat_filepath


def dl_audio(url, user_email, video_id):
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/media/'+f'{user_email}/'
    video_id_path = f'{video_id}/'
    single_video_dir = base_path+video_id_path
    if use_proxy:
        ydl_opts = {
            "proxy": "socks5://127.0.0.1:7890",
            "outtmpl": single_video_dir + f'{video_id}.mp3',
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
        }
    else:
        ydl_opts = {
            "outtmpl": single_video_dir + f'{video_id}.mp3',
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
        }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url)


@shared_task(bind=True)
def download_video(self, url_key, format_id):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url = str(redis_instance.hgetall(url_key)["url"])
    video_id = redis_instance.hgetall(url_key)["video_id"]
    user_email = redis_instance.hgetall(url_key)["user_email"]
    save_path = f"./media/{user_email}/{video_id}/"
    if VideoInfo.objects.get(video_id=video_id).video_dl_link is not None:
        current_file_path = VideoInfo.objects.get(video_id=video_id).video_dl_link
        if os.path.exists(current_file_path):
            os.remove(current_file_path)

    def finished_hook(d):
        # f = open('info_singlevideo_d.json', 'a+')
        # json.dump(d, f)
        # f.close()
        if d["status"] == "finished":
            format_note = d["info_dict"]["format_note"]
            if format_id in ["160", "133", "18", "135", "22", "137", "271", "313",] and d["info_dict"]["asr"] is None:
                dl_audio(url, user_email, video_id)
                video_dl_link = ffmpeg_concat(format_note, video_id, user_email)
            else:
                video_dl_link = base_dir + f"/media/{user_email}/{video_id}/n{video_id}-{format_note}.mp4"
                
            video_file_name = f"{video_id}-{format_note}.mp4"
            VideoInfo.objects.filter(video_id=video_id).update(
                video_dl_link=video_dl_link,
                video_file_name=video_file_name,
                video_downloaded_extension="mp4",
                video_downloaded_resolution=format_note,
                video_expiration_time_at=datetime.now() + timedelta(hours=24),
                video_is_downloaded=True,
            )
    if use_proxy:
        ydl_opts = {
            "proxy": "socks5://127.0.0.1:7890",
            "outtmpl": save_path + "n%(id)s-%(format_note)s.%(ext)s",
            "format": format_id,
            "progress_hooks": [finished_hook],
        }
    else:
        ydl_opts = {
            "outtmpl": save_path + "n%(id)s-%(format_note)s.%(ext)s",
            "format": format_id,
            "progress_hooks": [finished_hook],
        }
    url = redis_instance.hgetall(url_key)["url"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url)
    return "downloaded"

##
# End single video downloading process
##


##
# Start audio downloading process
##
@shared_task(bind=True)
def download_audio(self, url_key, ext, quality):
    video_id = redis_instance.hgetall(url_key)["video_id"]
    user_email = redis_instance.hgetall(url_key)["user_email"]
    save_path = f"./media/{user_email}/{video_id}/"
    if VideoInfo.objects.get(video_id=video_id).audio_dl_link is not None:
        current_file_path = VideoInfo.objects.get(
            video_id=video_id).audio_dl_link
        if os.path.exists(current_file_path):
            os.remove(current_file_path)

    def finished_hook(d):
        if d['status'] == 'finished':
            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            filename = video_id + "-" + quality + "." + ext
            filepath = base_dir + f"/media/{user_email}/{video_id}/" + filename
            VideoInfo.objects.filter(video_id=video_id).update(
                audio_dl_link=filepath,
                audio_file_name=filename,
                audio_downloaded_format=ext,
                audio_expiration_time_at=datetime.now() + timedelta(hours=24),
                audio_is_downloaded=True,
            )
    if use_proxy:
        ydl_opts = {
            "proxy": "socks5://127.0.0.1:7890",
            "outtmpl": save_path + "%(id)s-" + quality + ".%(ext)s",
            "format": "22",
            "progress_hooks": [finished_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": ext,
                    "preferredquality": quality,
                }
            ],
        }
    else:
        ydl_opts = {
            "outtmpl": save_path + "%(id)s-" + quality + ".%(ext)s",
            "format": "bestaudio/best",
            "progress_hooks": [finished_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": ext,
                    "preferredquality": quality,
                }
            ],
        }
    url = redis_instance.hgetall(url_key)["url"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url)
    return "finished"
##
# End audio downloading process
##

##
# Start playlist downloading process
##


@shared_task(bind=True)
def download_playlist_video_files(self, url_key, playlist_videos_info):
    playlist_id = redis_instance.hgetall(url_key)["playlist_id"]
    user_email = redis_instance.hgetall(url_key)["user_email"]
    for video_info in playlist_videos_info:
        video_id = video_info["video_id"]
        format_id = video_info["video_format_id"]
        format_note = video_info["video_format_note"]
        save_path = f"./media/{user_email}/{playlist_id}/{video_id}/"
        if VideoInfo.objects.get(video_id=video_id).video_dl_link is not None:
            current_file_path = VideoInfo.objects.get(
                video_id=video_id).video_dl_link
            if os.path.exists(current_file_path):
                os.remove(current_file_path)

        def finished_hook(d):
            if d["status"] == "finished":
                format_note = d["info_dict"]["format_note"]
                base_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))
                before_filename = f"{video_id}-{format_note}_noaudio.mp4"
                before_filepath = base_dir + \
                    f"/media/{user_email}/{playlist_id}/{video_id}/" + \
                    before_filename
                audio_path = base_dir + \
                    f"/media/{user_email}/{playlist_id}/{video_id}/" + \
                    f"{video_id}.mp3"
                input_video = ffmpeg.input(before_filepath)
                input_audio = ffmpeg.input(audio_path)
                ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
                    base_dir + f"/media/{user_email}/{playlist_id}/{video_id}/{video_id}-{format_note}.mp4").run(overwrite_output=True)
                after_filename = f"{video_id}-{format_note}.mp4"
                after_filepath = base_dir + \
                    f"/media/{user_email}/{playlist_id}/{video_id}/" + \
                    after_filename
                os.remove(before_filepath)
                VideoInfo.objects.filter(video_id=video_id).update(
                    video_dl_link=after_filepath,
                    video_file_name=after_filename,
                    video_downloaded_extension="mp4",
                    video_downloaded_resolution=format_note,
                    video_expiration_time_at=datetime.now() + timedelta(hours=24),
                    video_is_downloaded=True,
                )
        if use_proxy:
            ydl_opts = {
                "proxy": "socks5://127.0.0.1:7890",
                "outtmpl": save_path + "%(id)s-%(format_note)s_noaudio.%(ext)s",
                'format': str(format_id),
                "progress_hooks": [finished_hook],
            }
        else:
            ydl_opts = {
                "outtmpl": save_path + "%(id)s-%(format_note)s_noaudio.%(ext)s",
                'format': str(format_id),
                "progress_hooks": [finished_hook],
            }
        url = f'https://www.youtube.com/watch?v={video_id}'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url)
    return "downloaded"
##
# End playlist downloading process
##


@shared_task(bind=True)
def check_video_expired_link(self):
    videoinfo = VideoInfo.objects.all()
    # check expiration of downloaded video
    for video in videoinfo:
        # remove all of another info from downloaded video
        if video.video_is_downloaded == True:
            if video.video_expiration_time_at is not None:
                expiration_time = video.video_expiration_time_at - timezone.now()
                remaining_time_url = str(expiration_time)
                print(remaining_time_url)
                video.video_remaining_time_url = remaining_time_url.split(".")[
                    0]
                if expiration_time.total_seconds() <= 0:
                    # remove files from media
                    if video.video_dl_link is not None:
                        current_file_path = video.video_dl_link
                        if os.path.exists(current_file_path):
                            os.remove(current_file_path)
                    video.video_dl_link = ""
                    video.video_file_name = ""
                    video.video_downloaded_extension = ""
                    video.video_downloaded_resolution = ""
                    video.video_expiration_time_at = timezone.now()
                    video.video_remaining_time_url = ""
                    video.video_is_downloaded = False
                video.save()


@shared_task(bind=True)
def check_audio_expired_link(self):
    videoinfo = VideoInfo.objects.all()
    # check expiration of downloaded video
    for audio in videoinfo:
        # remove all of another info from downloaded video
        if audio.audio_is_downloaded == True:
            if audio.audio_expiration_time_at is not None:
                expiration_time = audio.audio_expiration_time_at - timezone.now()
                remaining_time_url = str(expiration_time)
                audio.audio_remaining_time_url = remaining_time_url.split(".")[
                    0]
                if expiration_time.total_seconds() <= 0:
                    # remove files from media
                    if audio.audio_dl_link is not None:
                        current_file_path = audio.audio_dl_link
                        if os.path.exists(current_file_path):
                            os.remove(current_file_path)
                    audio.audio_dl_link = ""
                    audio.audio_file_name = ""
                    audio.audio_downloaded_format = ""
                    audio.audio_expiration_time_at = timezone.now()
                    audio.audio_remaining_time_url = ""
                    audio.audio_is_downloaded = False
                audio.save()
