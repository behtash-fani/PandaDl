# Generated by Django 3.2.8 on 2021-12-11 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0007_videoinfo_video_downloaded_quality'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videoinfo',
            old_name='video_downloaded_format',
            new_name='video_downloaded_extension',
        ),
        migrations.RenameField(
            model_name='videoinfo',
            old_name='video_downloaded_quality',
            new_name='video_downloaded_resolution',
        ),
    ]
