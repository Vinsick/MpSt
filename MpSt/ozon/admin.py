from django.contrib import admin
from .models import *

class Ozon_SettingsAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'client_key', 'name')
    search_fields = ('client_id', 'client_key', 'name')
    list_filter = ('name',)

admin.site.register(Ozon_Settings, Ozon_SettingsAdmin)