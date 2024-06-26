# Generated by Django 5.0.3 on 2024-03-17 03:47

import main.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="media_mp3",
            field=models.ImageField(
                null=True, upload_to=main.models.get_image_upload_path_posts
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="user_pfp",
            field=models.ImageField(
                null=True, upload_to=main.models.get_image_upload_path_posts
            ),
        ),
        migrations.AlterField(
            model_name="userstats",
            name="banner",
            field=models.ImageField(
                null=True, upload_to=main.models.get_image_upload_path_profile
            ),
        ),
        migrations.AlterField(
            model_name="userstats",
            name="pfp",
            field=models.ImageField(
                null=True, upload_to=main.models.get_image_upload_path_profile
            ),
        ),
    ]
