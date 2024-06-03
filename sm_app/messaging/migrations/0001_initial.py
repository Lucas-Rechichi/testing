# Generated by Django 5.0.6 on 2024-06-03 07:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0026_post_day_of_creation'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('icon', models.ImageField(upload_to='')),
                ('room_bg_image', models.ImageField(upload_to='')),
                ('users', models.ManyToManyField(to='main.userstats')),
            ],
        ),
        migrations.CreateModel(
            name='ImageMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='messaging.chatroom')),
                ('sender', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.userstats')),
            ],
        ),
        migrations.CreateModel(
            name='TextMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='messaging.chatroom')),
                ('sender', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.userstats')),
            ],
        ),
        migrations.CreateModel(
            name='VideoMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='messaging.chatroom')),
                ('sender', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.userstats')),
            ],
        ),
    ]
