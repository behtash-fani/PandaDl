from django.urls import path
from . import views


app_name = 'accounts'
urlpatterns = [
    path("login/", views.user_login, name='user_login'),
    path("register/", views.user_register, name='user_register'),
    path("activate/<uidb64>/<token>/", views.user_activate, name='user_activate'),
    path("logout/", views.user_logout, name='user_logout'),
    path("forget_password/", views.forget_password, name='forget_password'),
    path("change_password/<uidb64>/<token>/", views.change_password, name='change_password'),
    path("dashboard/profile/", views.edit_profile, name='edit_profile'),
    path("downloads/all/", views.downloads_all, name='downloads_all'),
    path("downloads/audios/", views.downloads_audios, name='downloads_audios'),
    path("downloads/single-videos/", views.downloads_single_videos, name='downloads_single_videos'),
    path("downloads/playlists/", views.downloads_playlists, name='downloads_playlists'),
    path('download-file/<str:video_id>/<str:ext>/', views.download_file, name='download_file'),
]
