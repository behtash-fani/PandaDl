from rest_framework import serializers
from youtube.models import VideoInfo



class GetSingleVideoInfo(serializers.ModelSerializer):
    class Meta:
        model = VideoInfo
        fields = ('user','video_url','video_id','video_title','video_thumb_url','video_formats','video_dl_link','video_file_name','video_downloaded_extension','video_downloaded_resolution','video_expiration_time_at','video_is_downloaded',)
