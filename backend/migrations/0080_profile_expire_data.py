# Generated by Django 4.2.4 on 2024-10-26 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0079_remove_profile_is_online_profile_is_onedollar'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='expire_data',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]