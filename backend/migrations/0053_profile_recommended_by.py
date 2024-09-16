# Generated by Django 4.2.4 on 2024-09-16 04:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0052_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='recommended_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommended_profiles', to='backend.ref'),
        ),
    ]
