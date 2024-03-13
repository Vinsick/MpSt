from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main_mp, name="main_mp"),
    path('ozon/orders', views.ozon_orders, name="ozon_orders"),
    path('ozon/otgruzka/', views.ozon_otgruzka, name="ozon_otgruzka"),
    path('ozon/finance/otchet/', views.ozon_finance_otchet, name="ozon_finance_otchet"),

    path('ozon/spisok/upakovka/fbs/orders/<str:Date_End>/<str:Status>/<str:SpDostMain>/', views.ozon_fbs_ord, name="ozon_fbs_ord"),


    path('upakovka/spiski/', views.upakovka_spispki_index_html, name="upakovka_spispki_index_html"),
    path('upakovka/spiski/odrers/', views.orders_for_up_html, name="orders_for_up_html"),

    path('ozon/order_info/<str:posting_number>/', views.order_info, name='order_info'),
    path('ozon/spisok/', views.ozon_spisok, name="ozon_spisok"),
    path('ozon/marj/list/', views.ozon_marj, name="ozon_marj"),
    path('api/ozon/get_orders', views.ozon_get_orders, name="ozon_get_orders"),
    path('api/ozon/get_dost', views.ozon_get_dost, name="ozon_get_dost"),
    path('api/ozon/get_status', views.ozon_get_status, name="ozon_get_status"),
    path('api/ozon/get_orders_table', views.ozon_gets_orders_table, name="ozon_gets_orders_table"),
    path('api/products/add/', views.api_mp_products_add, name="api_mp_products_add"),
    path('api/products/get/', views.api_mp_products_get, name="api_mp_products_get"),
    path('api/ozon/finance/get/all/', views.api_mp_finance_get, name="api_mp_finance_get"),
    path('api/ozon/otgruzka/get/', views.api_ozon_get_otgruzka, name="api_ozon_get_otgruzka"),

    path('api/ozon/order/info/update/', views.api_ozon_info_update, name="api_ozon_info_update"),

    path('yandex/orders', views.yandex_orders, name="yandex_orders"),
    path('yandex/orders/<int:id_order>/', views.yandex_orders_info, name='yandex_orders_info'),
    path('yandex/orders/print/', views.yandex_orders_print, name="yandex_orders_print"),
    path('yandex/otgruzka/', views.yandex_otgruzka, name="yandex_otgruzka"),
    path('api/yandex/orders/update/all', views.yandex_orders_update_all, name="yandex_orders_update_all"),
    path('api/yandex/otgruzka/get/', views.api_yandex_get_otgruzka, name="api_yandex_get_otgruzka"),
    path('api/yandex/orders/get/', views.api_yandex_get_orders, name="api_yandex_get_orders"),
    path('api/yandex/order/info/update/', views.api_yandex_info_update, name="api_yandex_info_update"),

    path('products/views/<int:pk>/', views.ozon_products, name="ozon_products"),
    path('products/add/', views.ozon_products_add, name="ozon_products_add"),
    path('products/edit/<int:pk>/', views.ozon_products_add, name='ozon_products_edit'),
    path('products/<int:pk>/', views.v_products, name='v_products'),


    path('marjinalnost/', views.marja, name="marja"),

    path('sbermegamarket/', views.smm_index, name="smm_index"),
    path('sbermegamarket/otgruzka/', views.sbermegamarket_otgruzka, name="sbermegamarket_otgruzka"),
    path('sbermegamarket/orders/<int:id_order>/', views.sbermegamarket_orders_info, name='sbermegamarket_orders_info'),
    path('api/sbermegamarket/orders/update/all', views.sbermegamarket_orders_update_all, name="sbermegamarket_orders_update_all"),
    path('sbermegamarket/orders/print/', views.sbermegamarket_orders_print, name="sbermegamarket_orders_print"),
    path('api/sbermegamarket/otgruzka/get/', views.api_sbermegamarket_get_otgruzka, name="api_sbermegamarket_get_otgruzka"),
    path('api/sbermegamarket/orders/get/', views.api_sbermegamarket_get_orders, name="api_sbermegamarket_get_orders"),
    path('api/sbermegamarket/order/info/update/', views.api_sbermegamarket_info_update, name="api_sbermegamarket_info_update"),

    path('generate-marj-csv-ozon/', generate_csv_marj_ozon.as_view(), name='generate_csv_marj_ozon'),


    path('api/upakovka/spisok/generate/csv/', api_upakovka_spisok_generate_csv.as_view(), name='api_upakovka_spisok_generate_csv'),



    path('api/upakovka/spisok/table/all/', views.api_upakovka_get_all_orders_table, name="api_upakovka_get_all_orders_table"),
]