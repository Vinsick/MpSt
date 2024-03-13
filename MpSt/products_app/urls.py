from django.urls import path
from . import views


urlpatterns = [
    path('', views.product_main, name="product_main"),
]