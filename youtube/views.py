from __future__ import unicode_literals
from .tasks import extract_video_info,download_video, download_audio, download_playlist_video_files
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import youtube_download_form
from celery.result import AsyncResult
from django.http import JsonResponse
from django.conf import settings
from .models import VideoInfo
import redis
import uuid
import ast


redis_instance = redis.StrictRedis( host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, charset="utf-8", decode_responses=True,)

# download function # page 1
# @login_required(login_url="accounts:user_login")
def get_link(request):
    if not request.user.is_authenticated:
        messages.error(request, "To download the video from YouTube, please log in to your account or register on the site", 'warning')
        return redirect('accounts:user_login')
    url_key = uuid.uuid4().hex[:6].upper()
    if request.method == "POST":
        form = youtube_download_form(request.POST)
        if form.is_valid():
            url = form.cleaned_data["link_field"]
            redis_instance.hmset(url_key, {"user_email": request.user.email, "url": url})
            return redirect("youtube:initial_getinfo_progress", url_key)
    else:
        form = youtube_download_form()
    context = {"form": form}
    return render(request, "youtube/get_link.html", context)


# page 2 # middle page
# @login_required(login_url="accounts:user_login")
def initial_getinfo_progress(request, url_key):
    if not request.user.is_authenticated:
        messages.error(request, "To download the video from YouTube, please log in to your account or register on the site", 'warning')
        return redirect('accounts:user_login')
    extract_info_result = extract_video_info.delay(url_key)
    task_id = extract_info_result.task_id
    redis_instance.hmset(url_key, {"info_task_id": task_id})
    context = {"url_key": url_key}
    return render(request, "youtube/progress_getinfo.html", context)


def check_getinfo_status_task(request, url_key): # api endpoint for check status for get info from youtube video
    task_id = redis_instance.hgetall(url_key)["info_task_id"]
    res = AsyncResult(task_id,app=extract_video_info)
    return JsonResponse({'task_status':res.status})

# get and show info from video
def yt_download(request, url_key):
    # when sent playlist url for downloding
    url = redis_instance.hgetall(url_key)["url"]
    context = {}
    if "&list=" in url or "list=" in url:
        videos_id = redis_instance.hgetall(url_key)["videos_id"]
        videos_id_list = videos_id.split(",")
        videos_id_list.pop()
        for video_id in videos_id_list:
            video_info = VideoInfo.objects.filter(video_id=video_id)
            if len(video_info) > 1:
                for item in video_info[1:]:
                    item.delete()
        videos_info = VideoInfo.objects.filter(playlist_id=redis_instance.hgetall(url_key)["playlist_id"])
        context = {"url_key": url_key, "videos_info": videos_info}

    # when sent single video url for downloading 
    elif "?v=" in url and "&list=" not in url or 'youtu.be' in url and "&list=" not in url:
        video_id = redis_instance.hgetall(url_key)["video_id"]
        video_info = VideoInfo.objects.filter(video_id=video_id)
        if len(video_info) > 1:
            for item in video_info[1:]:
                item.delete()
        context = {"url_key": url_key, "video_info": video_info[0]}        

    return render(request, "youtube/show_info_download.html", context)


def download_video_progress(request, format_id, format_note, url_key):
    video_id = redis_instance.hgetall(url_key)["video_id"]
    video_info = VideoInfo.objects.get(video_id=video_id)
    download_video_result = download_video.delay(url_key, format_id)
    task_id = download_video_result.task_id
    redis_instance.hmset(url_key, {"dl_task_id": task_id})
    redis_instance.hmset(url_key, {"file_type": "single_video"})
    context = {"url_key": url_key, "video_id": video_id,"video_info": video_info,"file_type": "single_video",}
    return render(request, "youtube/progress_download_file.html", context)


def download_audio_progress(request, ext, quality, url_key):
    video_id = redis_instance.hgetall(url_key)["video_id"]
    video_info = VideoInfo.objects.get(video_id=video_id)
    download_audio_result = download_audio.delay(url_key, ext, quality)
    task_id = download_audio_result.task_id
    redis_instance.hmset(url_key, {"dl_task_id": task_id})
    redis_instance.hmset(url_key, {"file_type": "audio"})
    context = {"url_key": url_key, "video_id": video_id,"video_info": video_info,"file_type": "audio",}
    return render(request, "youtube/progress_download_file.html", context)


def download_playlist_video(request, url_key):
    playlist_videos_info = request.COOKIES[url_key]
    playlist_videos_info = ast.literal_eval(playlist_videos_info)
    download_playlist_video_result = download_playlist_video_files.delay(url_key, playlist_videos_info)
    task_id = download_playlist_video_result.task_id
    redis_instance.hmset(url_key, {"dl_task_id": task_id})
    redis_instance.hmset(url_key, {"file_type": "playlist_video"})
    context = {"url_key": url_key, "file_type": "playlist_video",}
    return render(request, "youtube/progress_download_file.html", context)

def check_dl_status_task(request, url_key):
    task_id = redis_instance.hgetall(url_key)["dl_task_id"]
    file_type = redis_instance.hgetall(url_key)["file_type"]

    if file_type == "single_video":
        res = AsyncResult(task_id,app=download_video)
    elif file_type == "audio":
        res = AsyncResult(task_id,app=download_audio)
    elif file_type == "playlist_video":
        res = AsyncResult(task_id,app=download_playlist_video_files)
    return JsonResponse({'dl_task_status':res.status})