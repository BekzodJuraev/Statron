# Generated by Django 4.2.4 on 2024-04-08 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_remove_add_chanel_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='chanel',
            name='daily_views',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='chanel',
            name='yesterday_subscribers',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='chanel',
            name='yesterday_views',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
