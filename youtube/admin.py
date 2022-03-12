from django.contrib import admin
from .models import VideoInfo



@admin.register(VideoInfo)
class VideoInfoAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'video_id', 'user', 'video_is_downloaded',)
