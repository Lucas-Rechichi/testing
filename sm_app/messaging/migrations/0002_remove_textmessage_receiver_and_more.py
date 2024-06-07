# Generated by Django 5.0.6 on 2024-06-07 09:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_rename_can_sign_up_arabaliconfigure_allowed'),
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textmessage',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='textmessage',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='videomessage',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='videomessage',
            name='sender',
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(null=True)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('video', models.FileField(null=True, upload_to='')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('reply', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='messaging.message')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messaging.chatroom')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.userstats')),
            ],
        ),
        migrations.DeleteModel(
            name='ImageMessage',
        ),
        migrations.DeleteModel(
            name='TextMessage',
        ),
        migrations.DeleteModel(
            name='VideoMessage',
        ),
    ]
