# Generated by Django 4.2.13 on 2024-06-26 16:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="visitorpass",
            name="gender",
        ),
    ]
