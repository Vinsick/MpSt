# Generated by Django 5.0.2 on 2024-02-16 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_alter_smmevent_eventdate_alter_smmevent_eventname_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='smm_settings',
            name='shop_id_api',
            field=models.CharField(max_length=50, null=True),
        ),
    ]