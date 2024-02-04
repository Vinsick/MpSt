from django.db import models

# Create your models here.
class WildBerries_Settings(models.Model):
    token = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.token
    

class WildBerries_Offices(models.Model):
    address = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    id = models.IntegerField(primary_key=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    selected = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class WildBerries_Seller_Offices(models.Model):
    name = models.CharField(max_length=255)
    officeId = models.ForeignKey(WildBerries_Offices, on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.name
    

class WildBerries_ParentCategory(models.Model):
    name = models.CharField(max_length=255)
    id = models.IntegerField(primary_key=True)
    isVisible = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class WildBerries_ContentObjects(models.Model):
      objectID = models.IntegerField(primary_key=True)
      parentID = models.ForeignKey(WildBerries_ParentCategory, on_delete=models.CASCADE)
      objectName = models.CharField(max_length=255)
      parentName = models.CharField(max_length=255) 
      isVisible = models.BooleanField(default=True)


class WildBerries_Income(models.Model):
    incomeId = models.IntegerField()
    number = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField()
    lastChangeDate = models.DateTimeField()
    supplierArticle = models.CharField(max_length=255)
    techSize = models.CharField(max_length=255)
    barcode = models.CharField(max_length=255)
    quantity = models.IntegerField()
    totalPrice = models.FloatField()
    dateClose = models.DateTimeField()
    warehouseName = models.CharField(max_length=255)
    nmId = models.IntegerField()
    status = models.CharField(max_length=255)

    def __str__(self):
        return self.supplierArticle
    

class WildBerries_Orders(models.Model):
    date = models.DateTimeField()
    lastChangeDate = models.DateTimeField()
    warehouseName = models.CharField(max_length=255)
    countryName = models.CharField(max_length=255)
    oblastOkrugName = models.CharField(max_length=255)
    regionName = models.CharField(max_length=255)
    supplierArticle = models.CharField(max_length=255)
    nmId = models.IntegerField()
    barcode = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    techSize = models.CharField(max_length=255)
    incomeID = models.IntegerField()
    isSupply = models.BooleanField()
    isRealization = models.BooleanField()
    totalPrice = models.FloatField()
    discountPercent = models.FloatField()
    spp = models.FloatField()
    finishedPrice = models.FloatField()
    priceWithDisc = models.FloatField()
    isCancel = models.BooleanField()
    cancelDate = models.DateTimeField()
    orderType = models.CharField(max_length=255)
    sticker = models.CharField(max_length=255)
    gNumber = models.CharField(max_length=255)
    srid = models.CharField(max_length=255)

