# Generated by Django 4.2.4 on 2024-10-25 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0074_paymentgateway_payment_status_payment_paymentgatway'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='paymentgatway',
        ),
    ]
