# Generated by Django 4.2.4 on 2024-04-26 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0028_remove_chanel_posts'),
    ]

    operations = [
        migrations.AddField(
            model_name='chanel',
            name='chanel_id',
            field=models.IntegerField(default=0),
        ),
    ]