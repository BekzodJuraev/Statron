# Generated by Django 4.2.4 on 2024-01-20 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_add_userbot'),
    ]

    operations = [
        migrations.AddField(
            model_name='chanel',
            name='add_chanel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.add_chanel'),
        ),
    ]
