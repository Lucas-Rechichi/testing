# Generated by Django 5.0.6 on 2024-06-05 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_alter_userstats_can_comment_alter_userstats_can_post_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstats',
            name='last_recorded_latitude',
            field=models.FloatField(default=50),
        ),
        migrations.AlterField(
            model_name='userstats',
            name='last_recorded_longitude',
            field=models.FloatField(default=100),
        ),
    ]
