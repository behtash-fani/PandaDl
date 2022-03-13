from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = "youtube"
urlpatterns = [
    path("get-link/", views.get_link, name="get_link"),
    path("refresh-link/<str:video_id>/", views.refresh_get_link, name="refresh_get_link"),
    path("<str:url_key>/waiting/",views.initial_getinfo_progress,name="initial_getinfo_progress",),
    path("<str:url_key>/download/", views.yt_download, name="yt_download"),
    path("<str:format_id>/<str:format_note>/<str:url_key>/dl-video/",views.download_video_progress,name="download_video_progress"),
    path("<str:ext>/<str:quality>/<str:url_key>/dl-audio/",views.download_audio_progress, name="download_audio_progress"),
    path("<str:url_key>/dl-playlist-video/",views.download_playlist_video,name="download_playlist_video",),
    path('<str:url_key>/getinfo-status/', views.check_getinfo_status_task, name="check_getinfo_status_task"),
    path('<str:url_key>/dl-status/', views.check_dl_status_task, name="check_dl_status_task"),
]
