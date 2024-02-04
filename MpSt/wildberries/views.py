from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.http import JsonResponse
from .models import * 
from django.contrib.auth import logout
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, FloatField
from datetime import timedelta, date
from calendar import monthrange
from django.db.models.functions import Coalesce, Cast
from django.db.models import DateTimeField
from django.db.models.functions import TruncDate
from django.db.models.functions import TruncDay
import requests
import json
import csv
import urllib.parse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Sum, Case, When
from django.contrib.auth.models import Group
import random
import string
import math
from django.db.models.functions import Round, Lower
from django.db.models.functions import TruncDay
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView
from django.contrib.auth.hashers import make_password
from django.utils import timezone


def wildberries_settings(request):
    if request.method == 'POST':
        # Получаем токен из POST-запроса
        token = request.POST.get('tokenInput')
        # Получаем объект настроек
        wb_set = WildBerries_Settings.objects.get(id=1)
        # Обновляем токен
        wb_set.token = token
        # Сохраняем изменения
        wb_set.save()
        # Перенаправляем пользователя обратно на страницу настроек
        return redirect('wildberries_settings')
    else:
        # Если это GET-запрос, то просто отображаем страницу настроек
        wb_set = WildBerries_Settings.objects.get(id=1)
        Wb_test = WildBerries()

        data = {
            'wb_set': wb_set
        }
        return render(request, 'main/settings.html', context=data)
    

def wildberries_incomes(request):
    BWC = WildBerries()

    WB_inc = WildBerries_Income.objects.all()

    data = {
        'WB_inc': WB_inc
        }
    return render(request, 'main/postavki.html', context=data)


def wildberries_stocks(request):
    BWC = WildBerries()

    data = {

        }
    return render(request, 'main/stocks.html', context=data)

def wildberries_orders(request):
    BWC = WildBerries()

    WB_inc = WildBerries_Orders.objects.all()
    data = {
        'WB_inc': WB_inc
        }
    return render(request, 'main/orders.html', context=data)

def wildberries_sales(request):
    BWC = WildBerries()

    data = {

        }
    return render(request, 'main/sales.html', context=data)



class WildBerries:
    def __init__(self):
        self.url = "https://suppliers-api.wildberries.ru"
        self.token = WildBerries_Settings.objects.get(id=1)
        self.headers = {
            'Authorization': self.token.token
        }

    def GetOffices(self):
        self.method = '/api/v3/offices'
        response = self.make_request(endpoint=self.method, method='GET')
        for item in response:
            # Извлекаем данные из каждого элемента
            address = item.get('address')
            name = item.get('name')
            city = item.get('city')
            location_id = item.get('id')
            longitude = item.get('longitude')
            latitude = item.get('latitude')
            selected = item.get('selected')
            
            # Проверяем, существует ли объект с таким id
            try:
                location = WildBerries_Offices.objects.get(id=location_id)
                # Обновляем объект, если он существует
                location.address = address
                location.name = name
                location.city = city
                location.longitude = longitude
                location.latitude = latitude
                location.selected = selected
                location.save()
            except WildBerries_Offices.DoesNotExist:
                # Создаем новый объект, если он не существует
                WildBerries_Offices.objects.create(
                    address=address,
                    name=name,
                    city=city,
                    id=location_id,
                    longitude=longitude,
                    latitude=latitude,
                    selected=selected
                )
        return response


    def GetWarehouses(self):
        self.method = '/api/v3/warehouses'
        response = self.make_request(endpoint=self.method, method='GET')
        for item in response:
                office_id = item.get('officeId')
                office = WildBerries_Offices.objects.get(id=office_id)
                seller_office = WildBerries_Seller_Offices(
                    name=item.get('name'),
                    officeId=office,
                    id=item.get('id')
                )
                seller_office.save()
        return response
    
    def update_or_create_orders(self, order_list):
        for order_data in order_list:
            # Преобразование строковых дат в объекты datetime
            order_data['date'] = timezone.make_aware(datetime.strptime(order_data['date'], "%Y-%m-%dT%H:%M:%S"))
            order_data['lastChangeDate'] = timezone.make_aware(datetime.strptime(order_data['lastChangeDate'], "%Y-%m-%dT%H:%M:%S"))
            order_data['cancelDate'] = timezone.make_aware(datetime.strptime(order_data['cancelDate'], "%Y-%m-%dT%H:%M:%S"))

            # Получение или создание объекта модели
            order, created = WildBerries_Orders.objects.update_or_create(
                nmId=order_data['nmId'],
                defaults=order_data
            )

    def GetOrders(self):
        self.url = "https://statistics-api.wildberries.ru"
        now = datetime.now()
        one_hour_ago = now - timedelta(days=30)
        formatted_date = one_hour_ago.strftime("%Y-%m-%d")
        self.method = f'/api/v1/supplier/orders?dateFrom={formatted_date}'
        response = self.make_request(endpoint=self.method, method='GET')
        self.update_or_create_orders(response)
        return response

    def GetIncomes(self):
        self.url = "https://statistics-api.wildberries.ru"
        now = datetime.now()
        one_hour_ago = now - timedelta(days=12)
        formatted_date = one_hour_ago.strftime("%Y-%m-%d")
        print(formatted_date)
        self.method = f'/api/v1/supplier/incomes?dateFrom={formatted_date}'
        response = self.make_request(endpoint=self.method, method='GET')
        print(response)
        for item in response:
                seller_office = WildBerries_Income(
                    incomeId=item.get('incomeId'),
                    number=item.get('number'),
                    date=item.get('date'),
                    lastChangeDate=item.get('lastChangeDate'),
                    supplierArticle=item.get('supplierArticle'),
                    techSize=item.get('techSize'),
                    barcode=item.get('barcode'),
                    quantity=item.get('quantity'),
                    totalPrice=item.get('totalPrice'),
                    dateClose=item.get('dateClose'),
                    warehouseName=item.get('warehouseName'),
                    nmId=item.get('nmId'),
                    status=item.get('status'),
                )
                seller_office.save()
        return response


    def Get_SpiSok_Objects(self):
        self.method = '/content/v2/object/all'
        WB_Parent_Categories_ = WildBerries_ParentCategory.objects.all()
        for i in WB_Parent_Categories_:
            print(i.id)
            data = {
                'locale': 'ru',
                'parentID': int(i.id)
            }
            response = self.make_request(endpoint=self.method, method='GET', data=data)
            print(response)
        return response

    def GetRoditelskiCategory(self):
        self.method = '/content/v2/object/parent/all'
        data = {
            'locale': 'ru'
        }
        response = self.make_request(endpoint=self.method, method='GET', data=data)
        for item in response['data']:
                seller_office = WildBerries_ParentCategory(
                    name=item.get('name'),
                    isVisible= item.get('isVisible'),
                    id=item.get('id')
                )
                seller_office.save()
        return response


    def make_request(self, endpoint, method, data=None, params=None, headers=None):
        if headers is not None:
            self.headers.update(headers)

        allowed_methods = ['GET', 'POST']
        if method not in allowed_methods:
            raise ValueError(f"Invalid method. Only {', '.join(allowed_methods)} are supported.")

        try:
            response = requests.request(method, self.url + endpoint, headers=self.headers, params=params, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except ValueError:
            print("Response could not be decoded as JSON.")
            return None