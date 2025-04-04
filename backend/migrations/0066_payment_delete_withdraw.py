# Generated by Django 4.2.4 on 2024-10-17 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0065_withdraw'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('wallet', models.CharField(max_length=200)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdraw', to='backend.profile')),
            ],
        ),
        migrations.DeleteModel(
            name='Withdraw',
        ),
    ]
