# Generated by Django 5.0.2 on 2024-05-11 23:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0014_alter_icf_a_alter_icf_k_alter_pcf_a_alter_pcf_k"),
    ]

    operations = [
        migrations.AlterField(
            model_name="interest",
            name="date_of_change",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="posttag",
            name="date_of_change",
            field=models.DateField(),
        ),
    ]
