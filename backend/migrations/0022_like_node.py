# Generated by Django 4.2.4 on 2024-04-22 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0021_subperhour'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='node',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
