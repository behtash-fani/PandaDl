# Generated by Django 3.2.8 on 2021-12-16 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(default='default_image.jpg', max_length=255, upload_to=''),
        ),
    ]
