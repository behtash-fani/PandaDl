# Generated by Django 3.2.8 on 2021-12-29 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0030_videoinfo_is_playlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='videoinfo',
            name='playlist_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='videoinfo',
            name='video_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
