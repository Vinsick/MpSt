# Generated by Django 5.0.2 on 2024-02-16 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_smmevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smmevent',
            name='eventDate',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='smmevent',
            name='eventName',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='smmevent',
            name='eventValue',
            field=models.CharField(max_length=255, null=True),
        ),
    ]