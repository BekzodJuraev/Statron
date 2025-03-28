# Generated by Django 4.2.4 on 2024-10-17 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0067_payment_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type_sub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribe', to='backend.profile')),
                ('type_sub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.type_sub')),
            ],
        ),
    ]
