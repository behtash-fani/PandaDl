from django.db import models
from accounts.models import User
from django.utils import timezone


class VideoInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    video_url = models.CharField(max_length=200, blank=True, null=True)
    playlist_id = models.CharField(max_length=100, blank=True, null=True)
    playlist_url = models.CharField(max_length=200, blank=True, null=True)
    is_playlist = models.BooleanField(default=False)
    video_id = models.CharField(max_length=100)
    video_title = models.CharField(max_length=100, blank=True, null=True)
    video_thumb_url = models.CharField(max_length=100, blank=True, null=True)
    video_formats = models.JSONField(blank=True, null=True)
    video_dl_link = models.CharField(max_length=200, blank=True, null=True)
    video_file_name = models.CharField(max_length=200, blank=True, null=True)
    video_downloaded_extension = models.CharField(max_length=200, blank=True, null=True)
    video_downloaded_resolution = models.CharField(max_length=200, blank=True, null=True)
    video_expiration_time_at = models.DateTimeField(blank=True, null=True)
    video_remaining_time_url = models.CharField(max_length=20, blank=True, null=True)
    video_is_downloaded = models.BooleanField(default=False)

    audio_dl_link = models.CharField(max_length=200, blank=True, null=True)
    audio_file_name = models.CharField(max_length=200, blank=True, null=True)
    audio_downloaded_format = models.CharField(max_length=200, blank=True, null=True)
    audio_bitrate = models.CharField(max_length=20, blank=True, null=True)
    audio_expiration_time_at = models.DateTimeField(blank=True, null=True)
    audio_remaining_time_url = models.CharField(max_length=20, blank=True, null=True)
    audio_is_downloaded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.video_title} - {self.video_id}"