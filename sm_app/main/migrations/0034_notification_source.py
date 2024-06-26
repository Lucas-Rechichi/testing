# Generated by Django 5.0.6 on 2024-06-14 21:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_messagenotificationsetting_and_more'),
        ('messaging', '0003_alter_chatroom_icon_alter_chatroom_room_bg_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='messaging.chatroom'),
            preserve_default=False,
        ),
    ]
