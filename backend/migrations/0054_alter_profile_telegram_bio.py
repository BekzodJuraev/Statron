# Generated by Django 4.2.4 on 2024-09-16 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0053_profile_recommended_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='telegram_bio',
            field=models.CharField(blank=True, default=None, max_length=150, null=True),
        ),
    ]
