from django.db import models


class Ozon_Settings(models.Model):
    client_id = models.CharField(max_length=30)
    client_key = models.CharField(max_length=50)
    name=models.CharField(max_length=50, null=True)