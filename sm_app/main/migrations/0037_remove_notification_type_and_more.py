# Generated by Django 5.0.6 on 2024-06-25 20:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_notification_type'),
        ('messaging', '0003_alter_chatroom_icon_alter_chatroom_room_bg_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='type',
        ),
        migrations.AddField(
            model_name='notification',
            name='relevant_message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='messaging.message'),
        ),
        migrations.AddField(
            model_name='notification',
            name='relevant_post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.post'),
        ),
    ]
