from django.urls import path
from . import views


urlpatterns = [
    path('ozon', views.ozon_main, name="ozon_main"),
    path('settings/', views.ozon_settings, name="ozon_settings"),
]