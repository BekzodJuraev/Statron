# Generated by Django 4.2.4 on 2024-04-22 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0024_alter_add_chanel_username_alter_like_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add_chanel',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='backend.profile'),
        ),
    ]
