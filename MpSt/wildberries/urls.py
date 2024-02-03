from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('settings/', views.wildberries_settings, name="wildberries_settings"),
    path('stocks/', views.wildberries_stocks, name="wildberries_stocks"),
    path('orders/', views.wildberries_orders, name="wildberries_orders"),
    path('sales/', views.wildberries_sales, name="wildberries_sales"),
    path('incomes/', views.wildberries_incomes, name="wildberries_incomes"),

]