from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.ozon_main_app, name="ozon_main_app"),
    path('settings', views.ozon_settings_app, name="ozon_settings_app"),



    path('products/<int:warehouse_id>/', views.ozon_products_app, name="ozon_products_app"),

    path('api/orders/update/', ozon_orders_settings_app, name='ozon_orders_settings_app'),
    path('api/orders/get/', api_ozon_orders_get_app, name='api_ozon_orders_get_app'),
    path('api/orders/update/one/', api_ozon_orders_update_one_app, name='api_ozon_orders_update_one_app'),
    path('orders/<int:warehouse_id>/', views.ozon_orders_app, name="ozon_orders_app"),
    path('orders/postings/<int:client_id>/<str:type_order>/<str:posting_number>', views.ozon_posting_view_app, name="ozon_posting_view_app"),


    path('reports', views.ozon_reports_app, name="ozon_reports_app"),
    path('api/reports/orders/upakovka/pdf', views.api_orders_upakovka_pdf_print, name="api_orders_upakovka_pdf_print"),


    path('warehouse/<int:warehouse_id>/', views.ozon_warehouse_app, name="ozon_warehouse_app"),
    path('api/warehouse/get', api_ozon_warehouse_get, name='api_ozon_warehouse_get'),




      
    path('api_key/add/', ozon_settings_edit, name='ozon_settings_add'),
    path('api_key/<int:pk>/edit/', ozon_settings_edit, name='ozon_settings_edit'),

    
]