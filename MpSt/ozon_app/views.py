import io
import os
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from .models import * 
from django.contrib.auth import logout
import requests
import json
import datetime
from django.db.models import CharField
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.forms.models import model_to_dict
from django.db.models import Case, When, Sum, F, FloatField, Value
import csv
import time
from collections import defaultdict
import urllib.parse
from django.db.models.functions import Round, Abs
from django.core import serializers
from django.db.models import Count
from django.db.models import Prefetch
import itertools
from django.db.models import ObjectDoesNotExist
from django.views import View
from django.shortcuts import get_object_or_404, render
from .models import OzonSettings
from .forms import *
from .ozon_api import OzonAPI
from .sctripts import *
from django.core import serializers
from django.core.serializers import serialize
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders




# Create your views here.
def check(request):
    if request.user.is_authenticated == True:
        return True
    else:
        return True
    
def ozon_main_app(request):
    if check(request)==True:

        return render(request, 'ozon_app/main.html')
    else:
        return redirect('main')
    

def ozon_settings_app(request):
    if check(request)==True:
        api_keys = OzonSettings.objects.all()
        data = {
            'api_keys': api_keys
        }
        return render(request, 'ozon_app/ozon_settings_app.html', context=data)
    else:
        return redirect('main')
    

def ozon_settings_edit(request, pk=None):
    if check(request)==True:
        if pk:
            ozon_settings = get_object_or_404(OzonSettings, pk=pk)
        else:
            ozon_settings = None

        if request.method == 'POST':
            if 'delete' in request.POST:  # Проверяем, есть ли кнопка удаления в POST запросе
                ozon_settings.delete()
                return redirect('ozon_settings_app')  # Перенаправляем на страницу со списком настроек
            else:
                form = OzonSettingsForm(request.POST, instance=ozon_settings)
                if form.is_valid():
                    ozon_settings = form.save(commit=False)  # Получаем объект без сохранения в базу данных
                    # Здесь вы можете выполнить дополнительные действия с объектом
                    ozon_settings.save()  # Сохраняем объект в базу данных
                    UpdateProductsList(ozon_settings)
                    UpdateWarehause(ozon_settings)
                    warehouses_list = OzonWarehouse.objects.filter(client_id=ozon_settings)
                    for warehouse in warehouses_list:
                        UpdateDeliveryMethod(warehouse.client_id, warehouse.warehouse_id)
                    return redirect('ozon_settings_app')  # Замените на ваш URL
        else:
            form = OzonSettingsForm(instance=ozon_settings)

        return render(request, 'ozon_app/settings/api_key_edit.html', {'form': form, 'ozon_settings': ozon_settings})
    else:
        return redirect('main')
    

def ozon_warehouse_app(request, warehouse_id=None):
    if check(request)==True:
        api_keys = OzonSettings.objects.all()
        if warehouse_id == 0:
            api_key_now = api_keys.first()
        else:
            api_key_now = OzonSettings.objects.get(client_id=warehouse_id)
        warehouses_list = OzonWarehouse.objects.filter(client_id=api_key_now)   
        data = {
            'key_now': api_key_now,
            'api_keys': api_keys,
            'warehouses_list': warehouses_list
        }
        return render(request, 'ozon_app/warehouse/warehouse_main.html', context=data)
    else:
        return redirect('main')
    


def api_ozon_warehouse_get(request):
    if check(request)==True:
        if request.method == 'GET':
            warehouseId = request.GET.get('warehouseId', None)
            warehouse = OzonWarehouse.objects.get(warehouse_id=warehouseId)
            dms = OzonDeliveryMethod.objects.filter(warehouse_id=warehouse)
            data = {
                'warehouse': serializers.serialize('json', [warehouse]),
                'dms': serializers.serialize('json', dms),
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)
    

def ozon_products_app(request, warehouse_id=None):
    if check(request)==True:
        api_keys = OzonSettings.objects.all()
        if warehouse_id == 0:
            api_key_now = api_keys.first()
        else:
            try:
                api_key_now = OzonSettings.objects.get(client_id=warehouse_id)
            except OzonSettings.DoesNotExist:
                return redirect('ozon_settings_app')



        ProductList = OzonProduct.objects.filter(client_id=api_key_now)

        data = {
            'key_now': api_key_now,
            'api_keys': api_keys,
            'ProductList': ProductList
        }
        return render(request, 'ozon_app/products/products_main.html', context=data)
    else:
        return redirect('main')
    


def ozon_orders_settings_app(request):
    if check(request)==True:
        if request.method == 'GET':
            client_id = request.GET.get('client_id', None)
            if client_id == '0':
                api_keys = OzonSettings.objects.all()
                for keys in api_keys:
                    Update_FBO_Posting_List(keys)
                    Update_FBS_Posting_List(keys)
            else:
                api_key_now = OzonSettings.objects.get(client_id=str(client_id))
                Update_FBO_Posting_List(api_key_now)
                Update_FBS_Posting_List(api_key_now)
            data = {
                'message': 'Заказы успешно обновлены',
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)
    


def ozon_orders_app(request, warehouse_id=None):
    if check(request)==True:

        api_keys = OzonSettings.objects.all()
        new_api_key = OzonSettings(client_id='0', client_key='0', name='Все')

        # Добавляем новый объект в список существующих объектов QuerySet
        api_keys = list(api_keys)  # Преобразуем QuerySet в список, чтобы можно было добавить новый объект
        api_keys.append(new_api_key)
        if warehouse_id == 0:

            api_key_now = api_keys[-1]
        else:
            try:
                api_key_now = OzonSettings.objects.get(client_id=warehouse_id)
            except OzonSettings.DoesNotExist:
                return redirect('ozon_settings_app')



        data = {
            'key_now': api_key_now,
            'api_keys': api_keys,
        }
        return render(request, 'ozon_app/orders/orders_main.html', context=data)
    else:
        return redirect('main')
    

def api_ozon_orders_get_app(request):
    if check(request)==True:
        if request.method == 'GET':
            filters = {}
            all_postings = []  # Создаем пустой список для хранения всех постингов

            date = datetime.datetime.today()
            date_to = date + datetime.timedelta(days=1)
            date_from= date_to - datetime.timedelta(21)


            order_type = request.GET.get('order_type', None)
            client_id = request.GET.get('client_id', None)

            create_date = request.GET.get('create_date', None)
            shipment_date = request.GET.get('shipment_date', None)
            status =  request.GET.get('status')


            date_range = create_date.split(' - ')
            if len(date_range) == 2:

                try:
                    date_from = datetime.datetime.strptime(date_range[0], "%d.%m.%Y")
                    date_to = datetime.datetime.strptime(date_range[1], "%d.%m.%Y")
                except ValueError:

                    pass
                else:
                    date_from = date_from.replace(hour=0, minute=0, second=1)
                    date_to = date_to.replace(hour=23, minute=59, second=59)
                    filters['in_process_at__gte'] = date_from.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    filters['in_process_at__lte'] = date_to.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                
                from_date = date_from.replace(hour=23, minute=59, second=59)
                date = date_to.replace(hour=0, minute=0, second=1)
                filters['in_process_at__gte'] = from_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                filters['in_process_at__lte'] = date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            

            try:
                status_son = json.loads(status)
            except:
                status_son = False
            
            if len(status_son['selectedValues_status_select']) > 0:
                filters['status'] = status_son['selectedValues_status_select']

            
            if order_type == 'true':



                if client_id == '0':
                    all_postings = get_FBS_orders(filters)
                else:
                    api_key_now = OzonSettings.objects.get(client_id=str(client_id))

                    filters['client_id']=api_key_now


                    all_postings = get_FBS_orders(filters)
                    
            else:
                print('fbo')

            all_postings = all_postings.order_by('-in_process_at')
            postings_data = []
            for posting in all_postings:
                posting_serialized = json.loads(serialize('json', [posting]))[0]
                products_serialized = json.loads(serialize('json', posting.ozon_fbs_posting_products_set.all()))
                posting_serialized['products'] = products_serialized
                postings_data.append(posting_serialized)
                    
            data = {
                'postings': postings_data,
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)
    




def ozon_posting_view_app(request, client_id=None, type_order=None, posting_number=None):
    if check(request)==True:

        api_key = OzonSettings.objects.get(id=client_id)

        if type_order == 'fbs':
            order = Ozon_FBS_Posting.objects.get(posting_number=posting_number, client_id=api_key)

        data = {
            'order': order
        }
        return render(request, 'ozon_app/orders/view_order.html', context=data)
    else:
        return redirect('main')
    

def api_ozon_orders_update_one_app(request):
    if check(request)==True:
        if request.method == 'GET':
            comment= request.GET.get('comment', None)
            date= request.GET.get('date', None)
            order_id= request.GET.get('order_id', None)
            client_id= request.GET.get('client_id', None)

            api_key = OzonSettings.objects.get(id=int(client_id))
            order = Ozon_FBS_Posting.objects.get(posting_number=order_id, client_id=api_key)

            order.system_comment = comment
            order.shipment_posting_date = date

            order.save()

            data = {
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)
    


def ozon_reports_app(request):
    if check(request)==True:
        unique_tpl_providers = Ozon_FBS_DeliveryMethod.objects.values_list('tpl_provider', flat=True).distinct()
        data={
            'tpl_providers': unique_tpl_providers
        }
        return render(request, 'ozon_app/reports/reports.html', context=data)
    else:
        return redirect('main')

def link_callback(uri, rel):
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
    else:
        path = None
    return path


def api_orders_upakovka_pdf_print(request):
    if not check(request):
        return redirect('main')

    filters = {}
    default_statuses = ['awaiting_packaging', 'awaiting_deliver']
    date = request.GET.get('date', None)
    status = request.GET.get('status', None)
    dostavka = request.GET.get('dostavka', None)
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
    date_obj = date_obj.replace(hour=23, minute=59, second=59, microsecond=59)
    formatted_date = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    filters['shipment_posting_date__lte'] = formatted_date

    status_son = json.loads(status) if status else False
    dostavka_son = json.loads(dostavka) if dostavka else False

    filters['status'] = status_son['selectedValues'] if status_son and len(status_son['selectedValues']) > 0 else default_statuses

    all_postings = get_FBS_orders(filters)

    if dostavka_son and len(dostavka_son['selectedValues']) > 0:
        all_postings = all_postings.filter(delivery_method__tpl_provider__in=dostavka_son['selectedValues'])

    postings_by_delivery_method = defaultdict(lambda: defaultdict(list))

    for posting in all_postings:
        if posting.delivery_method:
            for product in posting.ozon_fbs_posting_products_set.all():
                print(product.offer_id)
                try:
                    postings_by_delivery_method['Остальное'][posting.delivery_method.tpl_provider].append(posting)
                except:
                    postings_by_delivery_method['Остальное'][posting.delivery_method.tpl_provider].append(posting)

    # Преобразование defaultdict в обычный словарь
    postings_by_delivery_method = {
        category: {
            provider: postings for provider, postings in providers.items()
        } for category, providers in postings_by_delivery_method.items()
    }



    template = get_template('ozon_app/orders/api_orders_upakovka_pdf_print.html')
    context = {'postings_by_delivery_method': dict(postings_by_delivery_method)}
    html = template.render(context)
    result  = io.BytesIO()
    # Ensure the HTML is encoded in UTF-8
    html_encoded = html.encode("UTF-8")

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_encoded), result, encoding='UTF-8', link_callback=link_callback)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="report.pdf"'
        return response
    else:
        return HttpResponse('Ошибка при создании PDF: %s' % pdf.err)