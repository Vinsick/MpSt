from django.contrib import admin
from .models import *

@admin.register(WildBerries_Settings)
class WildBerries_SettingsAdmin(admin.ModelAdmin):
    list_display = ('token', 'last_updated')

@admin.register(WildBerries_Offices)
class WildBerries_OfficesAdmin(admin.ModelAdmin):
    list_display = ('address', 'name', 'city', 'id', 'longitude', 'latitude', 'selected')

@admin.register(WildBerries_Seller_Offices)
class WildBerries_Seller_OfficesAdmin(admin.ModelAdmin):
    list_display = ('name', 'officeId', 'id')

@admin.register(WildBerries_ParentCategory)
class WildBerries_ParentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'isVisible')

@admin.register(WildBerries_ContentObjects)
class WildBerries_ContentObjectsAdmin(admin.ModelAdmin):
    list_display = ('objectID', 'parentID', 'objectName', 'parentName', 'isVisible')

@admin.register(WildBerries_Income)
class WildBerries_IncomeAdmin(admin.ModelAdmin):
    list_display = ('incomeId', 'number', 'date', 'lastChangeDate', 'supplierArticle', 'techSize', 'barcode', 'quantity', 'totalPrice', 'dateClose', 'warehouseName', 'nmId', 'status')