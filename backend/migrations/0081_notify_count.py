# Generated by Django 4.2.4 on 2024-11-02 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0080_profile_expire_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='notify',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
