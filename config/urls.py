from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls', namespace='home')),
    path('youtube/', include('youtube.urls', namespace='youtube')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('celery-progress/', include('celery_progress.urls')),
    # path('api-auth/', include('rest_framework.urls')),
    # path('api/', include('youtube_api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)