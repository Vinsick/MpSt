# Generated by Django 5.0.2 on 2024-03-08 19:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ozon_app', '0007_alter_ozon_fbs_posting_delivering_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ozon_fbs_deliverymethod',
            name='fbs_posting',
        ),
        migrations.AddField(
            model_name='ozon_fbs_posting',
            name='delivery_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ozon_app.ozon_fbs_deliverymethod'),
        ),
    ]
