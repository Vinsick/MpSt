# Generated by Django 5.0.2 on 2024-02-16 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0005_smmshipment_id_shop_api_alter_ozonposting_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='smmshipment',
            name='packingDate',
            field=models.DateTimeField(null=True),
        ),
    ]