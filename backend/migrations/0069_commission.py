# Generated by Django 4.2.4 on 2024-10-18 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0068_type_sub_subscribe'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.ref')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commision', to='backend.profile')),
            ],
        ),
    ]
