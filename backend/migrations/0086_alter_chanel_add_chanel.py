# Generated by Django 4.2.4 on 2024-12-20 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0085_alter_add_chanel_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chanel',
            name='add_chanel',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.add_chanel'),
        ),
    ]
