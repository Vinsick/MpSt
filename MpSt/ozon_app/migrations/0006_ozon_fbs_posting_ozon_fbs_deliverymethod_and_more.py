# Generated by Django 5.0.2 on 2024-03-08 19:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ozon_app', '0005_ozonallpostingfinancialproduct_fbo_posting'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ozon_FBS_Posting',
            fields=[
                ('posting_number', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('poluchatel', models.CharField(blank=True, max_length=255)),
                ('delivering_date', models.DateTimeField()),
                ('in_process_at', models.DateTimeField()),
                ('is_express', models.BooleanField()),
                ('is_multibox', models.BooleanField()),
                ('multi_box_qty', models.IntegerField()),
                ('order_id', models.BigIntegerField()),
                ('order_number', models.CharField(max_length=255)),
                ('parent_posting_number', models.CharField(max_length=255)),
                ('shipment_date', models.DateTimeField()),
                ('status', models.CharField(max_length=255)),
                ('substatus', models.CharField(max_length=255)),
                ('tpl_integration_type', models.CharField(max_length=255)),
                ('tracking_number', models.CharField(max_length=255)),
                ('client_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ozon_app.ozonsettings')),
            ],
        ),
        migrations.CreateModel(
            name='Ozon_FBS_DeliveryMethod',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('tpl_provider', models.CharField(max_length=255)),
                ('tpl_provider_id', models.BigIntegerField()),
                ('warehouse', models.CharField(max_length=255)),
                ('warehouse_id', models.BigIntegerField()),
                ('fbs_posting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ozon_app.ozon_fbs_posting')),
            ],
        ),
        migrations.CreateModel(
            name='Ozon_FBS_analytics_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=200)),
                ('delivery_date_begin', models.DateTimeField()),
                ('delivery_date_end', models.DateTimeField()),
                ('delivery_type', models.CharField(max_length=200)),
                ('is_legal', models.BooleanField()),
                ('is_premium', models.BooleanField()),
                ('payment_type_group_name', models.CharField(max_length=200)),
                ('region', models.CharField(max_length=200)),
                ('tpl_provider', models.CharField(max_length=200)),
                ('tpl_provider_id', models.BigIntegerField()),
                ('warehouse', models.CharField(max_length=200)),
                ('warehouse_id', models.BigIntegerField()),
                ('fbs_posting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ozon_app.ozon_fbs_posting')),
            ],
        ),
        migrations.CreateModel(
            name='Ozon_FBS_Posting_Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_tail', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=255)),
                ('comment', models.CharField(blank=True, max_length=255)),
                ('country', models.CharField(blank=True, max_length=255)),
                ('district', models.CharField(blank=True, max_length=255)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('provider_pvz_code', models.CharField(blank=True, max_length=255)),
                ('pvz_code', models.IntegerField(blank=True, null=True)),
                ('region', models.CharField(blank=True, max_length=255)),
                ('zip_code', models.CharField(blank=True, max_length=255)),
                ('customer_email', models.EmailField(blank=True, max_length=254)),
                ('customer_id', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('phone', models.CharField(blank=True, max_length=255)),
                ('fbs_posting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ozon_app.ozon_fbs_posting')),
            ],
        ),
        migrations.CreateModel(
            name='Ozon_FBS_Posting_Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('offer_id', models.CharField(max_length=255)),
                ('price', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('sku', models.BigIntegerField()),
                ('currency_code', models.CharField(choices=[('RUB', 'Российский рубль'), ('BYN', 'Белорусский рубль'), ('KZT', 'Тенге'), ('EUR', 'Евро'), ('USD', 'Доллар США'), ('CNY', 'Юань')], max_length=3)),
                ('fbs_posting', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ozon_app.ozon_fbs_posting')),
            ],
        ),
    ]