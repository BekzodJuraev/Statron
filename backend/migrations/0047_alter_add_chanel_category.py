# Generated by Django 4.1.2 on 2024-06-12 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0046_add_chanel_category_alter_profile_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add_chanel',
            name='category',
            field=models.ManyToManyField(blank=True, to='backend.category_chanels'),
        ),
    ]
