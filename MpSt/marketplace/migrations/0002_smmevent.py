# Generated by Django 5.0.2 on 2024-02-16 09:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMMEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eventDate', models.DateTimeField()),
                ('eventName', models.CharField(max_length=255)),
                ('eventValue', models.CharField(max_length=255)),
                ('smm_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='smm_events', to='marketplace.smmitem')),
            ],
        ),
    ]