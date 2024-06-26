# Generated by Django 5.0.2 on 2024-05-11 22:15

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0011_alltag"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AllTag",
        ),
        migrations.AddField(
            model_name="interest",
            name="current_increace",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="interest",
            name="date_of_change",
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="interest",
            name="previous_increace",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="posttag",
            name="current_increace",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="posttag",
            name="date_of_change",
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="posttag",
            name="previous_increace",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
