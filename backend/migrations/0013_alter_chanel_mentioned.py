# Generated by Django 4.2.4 on 2024-04-06 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_chanel_mentioned_chanel_posts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chanel',
            name='mentioned',
            field=models.IntegerField(default=0),
        ),
    ]
