# Generated by Django 4.2.4 on 2024-10-25 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0078_alter_subscribe_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='is_online',
        ),
        migrations.AddField(
            model_name='profile',
            name='is_onedollar',
            field=models.BooleanField(default=True),
        ),
    ]
