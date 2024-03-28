# Generated by Django 5.0.3 on 2024-03-15 07:30

import django.db.models.deletion
import main.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Following",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subscribers", models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="LikedBy",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user_pfp",
                    models.ImageField(
                        null=True
                    ),
                ),
                ("title", models.CharField(max_length=150)),
                ("contents", models.TextField()),
                ("likes", models.IntegerField()),
                (
                    "media_mp3",
                    models.ImageField(
                        null=True
                    ),
                ),
                ("liked_by", models.ManyToManyField(to="main.likedby")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("followers", models.IntegerField()),
                (
                    "pfp",
                    models.ImageField(
                        null=True
                    ),
                ),
                (
                    "banner",
                    models.ImageField(
                        null=True
                    ),
                ),
                ("following", models.ManyToManyField(to="main.following")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
