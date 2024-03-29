# Generated by Django 5.0.2 on 2024-02-16 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_smm_settings_shop_id_api'),
    ]

    operations = [
        migrations.AddField(
            model_name='smmshipment',
            name='id_shop_api',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='ozonposting',
            name='products',
            field=models.ManyToManyField(blank=True, to='marketplace.ozonproduct'),
        ),
    ]
