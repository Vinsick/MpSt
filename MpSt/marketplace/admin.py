from django.contrib import admin
from .models import *

admin.site.register(Ozon_Settings)
admin.site.register(OzonCancellation)
admin.site.register(OzonDeliveryMethod)
admin.site.register(OzonAddress)
admin.site.register(OzonProduct)
admin.site.register(OzonPosting)
admin.site.register(OzonCustomer)
admin.site.register(Ozon_Status)
admin.site.register(Ozon_FinancialData)
admin.site.register(Ozon_PostingServices)
admin.site.register(Ozon_Products)
admin.site.register(Ozon_ItemServices)
admin.site.register(Ozon_Analytics_data)
admin.site.register(Ozon_Warehouse)


admin.site.register(YaBuyer)
admin.site.register(YaDelivery)
admin.site.register(YaItem)
admin.site.register(YaOrder)
admin.site.register(SMM_Settings)

class EventInline(admin.TabularInline):
    model = SMMEvent
    extra = 0
    ordering = ('eventDate',)  # Указываем, чтобы Event отображались в порядке возрастания eventDate

    def get_queryset(self, request):
        # Переопределяем метод get_queryset для сортировки Event по eventDate
        queryset = super().get_queryset(request)
        return queryset.order_by('eventDate')

class SMMGoodsDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_name', 'is_delivery', 'is_digital_mark_required')

class SMMCustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'address')


class SMMDiscountAdmin(admin.ModelAdmin):
    list_display = ('item', 'discountType', 'discountDescription', 'discountAmount')

admin.site.register(SMMGoodsData, SMMGoodsDataAdmin)
admin.site.register(SMMCustomer, SMMCustomerAdmin)


admin.site.register(SMMDiscount, SMMDiscountAdmin)


class SMMItemInline(admin.TabularInline):
    model = SMMItem
    extra = 0

@admin.register(SMMShipment)
class SMMShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipmentId', 'orderCode', 'status', 'customerFullName', 'customerAddress', 'shippingPoint', 'creationDate', 'deliveryDate')
    list_filter = ('status', 'shippingPoint', 'creationDate', 'deliveryDate')
    search_fields = ('shipmentId', 'orderCode', 'customerFullName', 'customerAddress')
    inlines = [SMMItemInline]

@admin.register(SMMItem)
class SMMItemAdmin(admin.ModelAdmin):
    list_display = ('itemIndex', 'status', 'subStatus', 'price', 'finalPrice', 'quantity', 'offerId', 'goodsId', 'boxIndex')
    list_filter = ('status', 'subStatus')
    search_fields = ('itemIndex', 'offerId', 'goodsId')
    raw_id_fields = ('shipment', 'goodsData')
    inlines = [EventInline]

admin.site.register(SMMEvent)


class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic

class MpProductAdmin(admin.ModelAdmin):
    list_display = ('artikul', 'category', 'kol', 'sebestoimost')
    list_filter = ('category',)
    search_fields = ('artikul', 'category__name')
    inlines = [
        ProductCharacteristicInline,
    ]

admin.site.register(MpProduct, MpProductAdmin)
admin.site.register(Category)
admin.site.register(Characteristic)


class Ozon_ProductListAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'offer_id', 'client_id', 'sku')
    list_filter = ('client_id',)
    search_fields = ('product_id', 'offer_id', 'sku')

admin.site.register(Ozon_ProductList, Ozon_ProductListAdmin)