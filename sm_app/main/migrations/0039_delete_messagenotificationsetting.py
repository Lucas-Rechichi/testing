# Generated by Django 5.0.6 on 2024-07-13 23:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0038_notification_relevant_poll"),
    ]

    operations = [
        migrations.DeleteModel(
            name="MessageNotificationSetting",
        ),
    ]
