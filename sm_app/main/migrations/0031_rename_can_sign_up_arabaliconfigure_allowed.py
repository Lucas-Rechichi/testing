# Generated by Django 5.0.6 on 2024-06-05 09:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_arabaliconfigure'),
    ]

    operations = [
        migrations.RenameField(
            model_name='arabaliconfigure',
            old_name='can_sign_up',
            new_name='allowed',
        ),
    ]
