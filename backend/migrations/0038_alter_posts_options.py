# Generated by Django 4.2.4 on 2024-05-17 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0037_alter_posts_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='posts',
            options={'ordering': ['date']},
        ),
    ]
