# Generated by Django 4.2.4 on 2024-12-20 12:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0086_alter_chanel_add_chanel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chanel',
            name='username',
        ),
    ]