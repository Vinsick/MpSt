# Generated by Django 5.0.2 on 2024-03-08 20:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ozon_app', '0009_ozon_fbs_deliverymethod_client_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='ozonallpostingfinancialproduct',
            name='fbs_posting',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ozon_app.ozon_fbs_posting'),
        ),
    ]
