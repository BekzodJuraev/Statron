# Generated by Django 4.2.4 on 2024-05-17 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0042_alter_mentions_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mentions',
            options={'ordering': ['-post__date']},
        ),
    ]
