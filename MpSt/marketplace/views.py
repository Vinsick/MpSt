from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from .models import * 
from app.models import * 
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
from .forms import *
from django.db.models import Count
from django.db.models import Prefetch
import itertools
from django.db.models import ObjectDoesNotExist
from django.views import View


# Create your views here.
def check(request):
    if request.user.is_authenticated == True:
        return True
    else:
        return False
    
def main_mp(request):
    if check(request)==True:

        return render(request, 'marketplace/main.html')
    else:
        return redirect('login')
    
def orders_for_up_html(request):
    if check(request)==True:

        return render(request, 'marketplace/upakovka/orders_for_up.html')
    else:
        return redirect('login')


def upakovka_spispki_index_html(request):
    if check(request)==True:

        return render(request, 'marketplace/upakovka/spiski.html')
    else:
        return redirect('login')


def api_upakovka_get_all_orders_table(request):
    if check(request)==True:
        if request.method == 'GET':

            data = {
                'status': '200'
            }

            report_date = request.GET.get('report_date', None)
            positions_type = request.GET.get('positions_type', None)

            marketplaces_list = request.GET.get('marketplaces_list')
            try:
                marketplaces_list_json = json.loads(marketplaces_list)

            except json.JSONDecodeError:
                print("Ошибка: строка не является допустимой JSON-строкой.")

            if "ozon" in marketplaces_list_json['status_select'] or not marketplaces_list_json.get('status_select'):     
                # Преобразование строковой даты в datetime
                Date_End = datetime.datetime.strptime(report_date, '%Y-%m-%d') + datetime.timedelta(1)

                OzonPostings = OzonPosting.objects.filter(shipment_posting_date__lte=Date_End, status='awaiting_deliver').values_list(
                    'posting_number', 'order_id', 'order_number', 'status', 'delivery_method',
                    'tracking_number', 'tpl_integration_type', 'in_process_at', 'shipment_date',
                    'delivering_date', 'cancellation', 'customer__name', 'products', 'substatus',
                    'mandatory_mark', 'parent_posting_number', 'prr_option', 'multi_box_qty',
                    'is_multibox', 'substatus', 'prr_option', 'is_express', 'addressee',
                    'barcodes', 'analytics_data', 'available_actions', 'requirements'
                ).order_by('-in_process_at')

                


                formatted_postings = []
                for posting in OzonPostings:
                    formatted_posting = list(posting)
                    formatted_posting[7] = posting[7].strftime('%d.%m.%Y') if posting[7] else None  # in_process_at
                    formatted_posting[8] = posting[8].strftime('%d.%m.%Y') if posting[8] else None  # shipment_date
                    formatted_posting[9] = posting[9].strftime('%d.%m.%Y') if posting[9] else None  # delivering_date
                    id = posting[0]
                    order = OzonPosting.objects.get(posting_number=id)
                    financial_data = Ozon_FinancialData.objects.get(ozon_posting=order)
                    products = financial_data.financialll_data_product.all()
                    txt = ""
                    is_first_iteration = True
                    add_to_formatted_postings = False

                    for i in products:
                        try:
                            get = Ozon_ProductList.objects.get(product_id=i.product_id)
                            try:
                                product = MpProduct.objects.get(artikul=get.offer_id)
                                if positions_type == 'chairs' and product.category.name == "Стул":
                                    add_to_formatted_postings = True
                                if positions_type == 'without_chairs' and product.category.name != "Стул":
                                    add_to_formatted_postings = True
                                    
                                if not is_first_iteration:
                                    txt += ', '
                                txt += product.artikul
                                is_first_iteration = False
                            except ObjectDoesNotExist:
                                if not is_first_iteration:
                                    txt += ', '
                                txt += 'Ошибка 2'
                                is_first_iteration = False
                        except:
                            if not is_first_iteration:
                                txt += ', '
                            txt += 'Ошибка 1'
                            is_first_iteration = False
                    
                    if add_to_formatted_postings is True:
                        formatted_posting.append(txt)
                        formatted_posting.append('Ozon')
                        formatted_posting.append(order.delivery_method.tpl_provider)
                        formatted_postings.append(formatted_posting)
                

                data['Orders_ozon'] = formatted_postings


            if "ya_market" in marketplaces_list_json['status_select'] or not marketplaces_list_json.get('status_select'):
                if report_date is not None:
                    report_date_datetime = datetime.datetime.strptime(report_date, '%Y-%m-%d')  # конвертируем строку в объект datetime
                    report_date_plus_one_day = report_date_datetime  # добавляем день

                if report_date:
                    filters = {'status': 'PROCESSING', 'shipmentDate__lte': report_date_plus_one_day}
                else:
                    filters = {'status': 'PROCESSING'}

                # Load all order_list with related items
                order_list = YaOrder.objects.filter(**filters).order_by('shipmentDate').exclude(substatus='SHIPPED')



                orders_values = list(order_list.values_list(
                    'id_order',
                    'status',
                    'substatus',
                    'creation_date',
                    'items_total',
                    'total',
                    'delivery_total',
                    'subsidy_total',
                    'total_with_subsidy',
                    'buyer_items_total',
                    'buyer_total',
                    'buyer_items_total_before_discount',
                    'buyer_total_before_discount',
                    'payment_type',
                    'payment_method',
                    'fake',
                    'id_shop',
                    'shipmentDate',
                    'shipment_posting_date',
                    named=True  # This will return namedtuples instead of regular tuples
                ))
                # Convert the Row objects to dictionaries
                orders_dicts_yandex = [order._asdict() for order in orders_values]

                formatted_orders = []

                for order_dict in orders_dicts_yandex:
                    txt = ''
                    order_id = order_dict['id_order']  # Assuming 'id_order' is the primary key of the order
                    order = YaOrder.objects.get(id_order=order_id)
                    items = YaItem.objects.filter(ya_order=order)  # Assuming the Item model is related to the order via ForeignKey
                    
                    add_to_formatted_postings = False
                    txt = [f'{item.offer_id}: {item.count}' for item in items]
                    for item in items:
                        try:
                            art = MpProduct.objects.get(artikul=item.offer_id)
                            if positions_type == 'chairs' and art.category.name == "Стул":
                                add_to_formatted_postings = True
                                break
                            elif positions_type == 'without_chairs' and art.category.name != "Стул":
                                add_to_formatted_postings = True
                                break
                        except MpProduct.DoesNotExist:
                            break
                    
                    if add_to_formatted_postings:
                        order_dict['txt'] = txt  # Add the 'txt' attribute to the dictionary
                        order_dict['marketplace'] = 'Я.Маркет'
                        formatted_orders.append(order_dict)

                # Now formatted_orders contains the orders that meet the criteria
                data['Orders_ya'] = formatted_orders

            if "smm" in marketplaces_list_json['status_select'] or not marketplaces_list_json.get('status_select'):
                if report_date is not None:
                    report_date_datetime = datetime.datetime.strptime(report_date, '%Y-%m-%d')  # конвертируем строку в объект datetime
                    report_date_plus_one_day = report_date_datetime + timedelta(days=1)  # добавляем день

            
                if report_date:
                    filters = {'status__in': ['CONFIRMED', 'NEW', 'PENDING', 'PACKED'], 'shipmentDateFrom__lte': report_date_plus_one_day}
                else:
                    filters = {'status__in': ['CONFIRMED', 'NEW', 'PENDING', 'PACKED']}

                orders_smm = SMMShipment.objects.filter(**filters)

                orders_values__smm = list(orders_smm.values_list(
                    'shipmentId',
                    'orderCode',
                    'confirmedTimeLimit',
                    'packingTimeLimit',
                    'shippingTimeLimit',
                    'shipmentDateFrom',
                    'shipmentDateTo',
                    'deliveryId',
                    'shipmentDateShift',
                    'shipmentIsChangeable',
                    'customerFullName',
                    'customerAddress',
                    'shippingPoint',
                    'creationDate',
                    'deliveryDate',
                    'deliveryDateFrom',
                    'deliveryDateTo',
                    'deliveryMethodId',
                    'depositedAmount',
                    'status',
                    'shipment_posting_date',
                    'system_comment',
                    named=True  # This will return namedtuples instead of regular tuples
                ))
                # Convert the Row objects to dictionaries
                orders_dicts_smm = [order._asdict() for order in orders_values__smm]

                formatted_orders = []
                for order_dict in orders_dicts_smm:
                    order_id = order_dict['shipmentId']  # Assuming 'id_order' is the primary key of the order
                    order = SMMShipment.objects.get(shipmentId=order_id)
                    items = SMMItem.objects.filter(shipment=order)  # Assuming the Item model is related to the order via ForeignKey
                    add_to_formatted_postings = False
                    txt = [f'{item.offerId}: {item.quantity}' for item in items]
                    for item in items:
                        try:
                            art = MpProduct.objects.get(artikul=item.offerId)
                            if positions_type == 'chairs' and art.category.name == "Стул":
                                add_to_formatted_postings = True
                                break
                            elif positions_type == 'without_chairs' and art.category.name != "Стул":
                                add_to_formatted_postings = True
                                break
                        except MpProduct.DoesNotExist:
                            break
                    
                    if add_to_formatted_postings:
                        print(order_dict['shippingPoint'])
                        if order_dict['shippingPoint'] == '96775':
                            order_dict['type'] = 'Почта России'
                        else:
                            order_dict['type'] = 'Сбер'
                        order_dict['txt'] = txt  # Add the 'txt' attribute to the dictionary
                        order_dict['marketplace'] = 'СММ'
                        formatted_orders.append(order_dict)
                data['Orders_smm'] = formatted_orders


            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)



def ozon_orders(request):
    if check(request)==True:
        return render(request, 'marketplace/ozon/ozon_orders.html')
    else:
        return redirect('login')
    
def ozon_spisok(request):
    if check(request)==True:
        return render(request, 'marketplace/ozon/ozon_spisok.html')
    else:
        return redirect('login')
    
def ozon_products(request, pk):
    if check(request)==True:
        category = Category.objects.get(id=pk)
        all_prod = MpProduct.objects.filter(category=category).prefetch_related('productcharacteristic_set')

        # Получаем все ProductCharacteristic, связанные с MpProduct
        product_characteristics = ProductCharacteristic.objects.filter(product__in=all_prod)

        # Получаем уникальные имена характеристик
        characteristic_names = product_characteristics.values_list('characteristic__name', flat=True).distinct()

        categories_list = MpProduct.objects.values('category__name', 'category').annotate(count=Count('id')).order_by('-count')

        # Преобразуем QuerySet в список, чтобы можно было итерироваться и изменять
        all_prod_list = list(all_prod)

        all_prod_with_chars = []

        for product in all_prod:
            product_chars = {}
            for characteristic in product.productcharacteristic_set.all():
                for i in characteristic_names:
                    if i == characteristic.characteristic.name:
                        product_chars[i] = characteristic.value
            # Добавляем прочерк для характеристик, которых нет в product_chars
            for i in characteristic_names:
                if i not in product_chars:
                    product_chars[i] = '-'
            all_prod_with_chars.append({'product': product, 'characteristics': product_chars})


        data = {
            'all_prod':all_prod_with_chars,
            'categories_list': categories_list,
            'characteristic_names': characteristic_names
        }
        return render(request, 'marketplace/ozon/ozon_products.html', context=data)
    else:
        return redirect('login')
    
def ozon_products_add(request, pk=None):
    if check(request):
        if pk:
            product = get_object_or_404(MpProduct, pk=pk)
        else:
            product = MpProduct()
        
        if request.method == 'POST':
            
            form = MpProductForm(request.POST, instance=product)
            
            # Bind the formset to the POST data
            formset = CharacteristicFormSet(request.POST, prefix='characteristic')
 
            if form.is_valid() and formset.is_valid():
                created_product = form.save()

                # Delete existing characteristics for the product
                ProductCharacteristic.objects.filter(product=created_product).delete()
                # Save the new characteristics
                for form in formset:
                    if form.cleaned_data.get('characteristic') and form.cleaned_data.get('value'):
                        characteristic = form.cleaned_data['characteristic']
                        value = form.cleaned_data['value']
                        ProductCharacteristic.objects.create(product=created_product, characteristic=characteristic, value=value)

                # Redirect to product detail view or according to your flow
                return redirect('v_products', pk=created_product.pk)
            else:
                print("Formset errors: " + formset.errors)
        else:
            form = MpProductForm(instance=product)
            # Get all characteristics for the product
            characteristics = ProductCharacteristic.objects.filter(product=product)
            # Bind the formset to the initial data
            formset = CharacteristicFormSet(prefix='characteristic', initial=[{'characteristic': c.characteristic, 'value': c.value} for c in characteristics])

        return render(request, 'marketplace/ozon/ozon_products_add.html', {
            'form': form,
            'formset': formset
        })
    
    else:
        return redirect('login')
    



def get_sebest():
    return


def v_products(request, pk):
    if check(request)==True:
        product = get_object_or_404(MpProduct, id=pk)
        OzonData = Ozon()
        Ozon_Prod_Info = OzonData.GetProdInfo(product.artikul)
        context = {
            'product': product,
            'Ozon_Prod_Info':Ozon_Prod_Info
        }

        return render(request, 'marketplace/v_products.html', context)
    else:
        return redirect('login')

def ozon_finance_otchet(request):
    if check(request)==True:
        return render(request, 'marketplace/ozon_finance_otchet.html')
    else:
        return redirect('login')

def OzonGetProInfoMarvaV2(sku, client_id, sp_dost):
    OzonClient = Ozon()
    sku=sku
    prodinfo = OzonClient.GetProductInJoMarja(client_id=client_id, sku_list=sku)
    ofer_list = []
    for skus in sku:
        for profInfo in prodinfo['result']:

            if 'offer_id' in profInfo:

                if skus['sku'] == profInfo['fbo_sku'] or skus['sku'] == profInfo['fbs_sku'] or skus['sku'] == profInfo['sku']:
                    ofer_list.append(profInfo['offer_id'])
                    skus['offer_id']=profInfo['offer_id']
                    skus['precent'] = profInfo['vat']
                    skus['name'] = profInfo['name']
                    comissions = profInfo['commissions']
                    if skus['del_meth'] == None:
                        sp_dost = "fbo"
                    if skus['del_meth'] == False:
                        sp_dost= "fbs"
                    if skus['del_meth'] == True:
                        sp_dost= "rfbs"
                    for com in comissions:
                        if com['sale_schema'] == sp_dost.lower():
                            skus['comission'] = com['value']

    prodinfoMile = OzonClient.GetProductInToMile(client_id=client_id, sku=ofer_list)

    for skus in sku:
        for profInfo in prodinfoMile['result']['items']:
            if 'offer_id' in skus:
                skus['offer_id'] = skus['offer_id']
                
            else:
                skus['offer_id'] = 'Ошибка в получении верного SKU: ' + str(skus['sku'])
                skus['precent'] = "0.200000"
                skus['comission'] = 0
                skus['summ'] = 0
                skus['name'] = 'Ошибка в получении верного SKU: ' + str(skus['sku'])

            if skus['offer_id'] == profInfo['offer_id']:
                if skus['del_meth'] == None:
                    summ = float(profInfo['commissions']['fbo_fulfillment_amount']) + float(profInfo['commissions']['fbo_direct_flow_trans_max_amount'])+ float(profInfo['commissions']['fbo_deliv_to_customer_amount'])+ float(profInfo['commissions']['fbo_return_flow_trans_max_amount'])
                    skus['summ'] = summ
                        
                if skus['del_meth'] == False:
                    summ = float(profInfo['commissions']['fbs_first_mile_max_amount']) + float(profInfo['commissions']['fbs_direct_flow_trans_max_amount'])+ float(profInfo['commissions']['fbs_deliv_to_customer_amount'])
                    skus['summ'] = summ

                if skus['del_meth'] == True:
                    summ = 0
                    skus['summ'] = summ

    return sku

def get_date(date_str, date_format):
    if date_str:
        return datetime.datetime.strptime(date_str, date_format).strftime(date_format)
    return None


def api_ozon_get_otgruzka(request):
    if check(request)==True:
        if request.method == 'GET':
            client_id = request.GET.get('sp_dot', "all")
            if client_id == "Все":
                client_id = None
            else:
                client_id = Ozon_Settings.objects.get(name=client_id).client_id

            date_start_str = request.GET.get('date_start', '')
            date_end_str = request.GET.get('date_end', '')
            date_format = '%Y-%m-%d'

            filters = {
                'delivery_method__isnull': False
            }

            if date_start_str == date_end_str:
                filters['delivering_date__date'] = date_start_str
            else:
                filters['delivering_date__range'] = (date_start_str, date_end_str)

            if client_id is not None:
                filters['client_id'] = client_id
            
            ozon_orders = OzonPosting.objects.filter(**filters).exclude(status="cancelled")
  
            ozon_prod = ozon_orders.values(
                sku=F('financialll_data__financialll_data_product__product_id'),
                ).exclude(
                    sku=None
                ).annotate(
                quantity_sum=Sum(Case(
                    When(financialll_data__financialll_data_product__quantity__gt=0, then='financialll_data__financialll_data_product__quantity'),
                    default=Value(1)
                )),
                price_sum=Sum('financialll_data__financialll_data_product__price'),
                client_id=F('client_id')
            ).order_by('sku')

            total_quantity = ozon_prod.aggregate(total_quantity=Sum('quantity_sum'))
            total_sum = ozon_prod.aggregate(total_sum=Sum('price_sum'))

            for sku in ozon_prod:
                try:
                    product = Ozon_ProductList.objects.get(sku=sku['sku'])
                    sku['sku']=product.offer_id
                except Ozon_ProductList.DoesNotExist:
                    oc = Ozon()
                    tt = oc.GetProdInfo(sku=sku['sku'], offer_id=None, client_id=sku['client_id'])
                    OzonClients = Ozon_Settings.objects.all()
                    if tt is None:    
                        for OzonClient in OzonClients:
                            try:
                                tt = oc.GetProdInfo(sku=sku['sku'], offer_id=None, client_id=OzonClient.client_id)
                            except:
                                print('не найдено')

                    
                    if tt is not None:  
                        prod, _ = Ozon_ProductList.objects.update_or_create(
                            product_id=sku['sku'],
                            defaults={
                                'offer_id': tt['result']['offer_id'],
                                'sku': sku['sku'],
                                'client_id': sku['client_id']
                            }
                        )
                        prod.save()
                        product = Ozon_ProductList.objects.get(sku=sku['sku'])
                        sku['sku']=product.offer_id

            data = {
                'total_quantity': total_quantity,
                'total_sum': total_sum,
                'ozon_orders': list(ozon_prod),
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)




def api_yandex_get_otgruzka(request):
    if check(request)==True:
        if request.method == 'GET':
            client_id = request.GET.get('sp_dot', "all")
            if client_id == "all":
                client_id = None
            else:
                client_id = request.GET.get('sp_dot', "all")

            filters= {}
            date_start_str = request.GET.get('date_start', '')
            date_end_str = request.GET.get('date_end', '')

            # Если даты одинаковые, используем одну дату для фильтрации
            if date_start_str == date_end_str:
                date_str = date_start_str  # Или date_end_str, они одинаковые
                start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                end_date = start_date
            else:
                start_date = datetime.datetime.strptime(date_start_str, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(date_end_str, '%Y-%m-%d')
                end_date = end_date.replace(hour=23, minute=59, second=59)

            if start_date > end_date:
                start_date_1 = start_date
                start_date = end_date
                end_date = start_date_1

            filters['ya_order__shipmentDate__range'] = [start_date, end_date]


            if client_id != None:
                filters['ya_order__id_shop'] = request.GET.get('sp_dot', '')


            # Получите уникальные offer_id и сумму count таких же offer_id
            result = YaItem.objects.filter(ya_order__shipmentDate__isnull=False, **filters).exclude(ya_order__status__in=['CANCELLED', 'UNPAID']).values('offer_id').annotate(total_count=Sum('count'), total_price=Sum('price'))

            result_total = YaItem.objects.filter(ya_order__shipmentDate__isnull=False, **filters).exclude(ya_order__status__in=['CANCELLED', 'UNPAID']).aggregate(total_count=Sum('count'), total_price=Sum('price'))

            if result_total['total_count'] == None:
                result_total['total_count'] = 0

            if result_total['total_price'] == None:
                result_total['total_price'] = 0
            data = {
                'result_total': result_total,
                'ozon_orders': list(result),
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)


def yandex_otgruzka(request):
    if check(request):
        unique_id_shops = YaOrder.objects.values_list('id_shop', flat=True).distinct()
        class_obj = YaMarket()
        shops = []
        for shop in unique_id_shops:
            shop_info = class_obj.GetShopInfo(shop)
            shop_info_ = {
                'id': shop,
                'name': shop_info['campaign']['business']['name']
            }
            shops.append(shop_info_)

        data = {
            'unique_id_shops':unique_id_shops,
            'shops': shops
            }
        return render(request, 'marketplace/yamarket/ya_otgruzka.html', context=data)

    return redirect('login')


def api_sbermegamarket_get_otgruzka(request):
    if check(request)==True:
        if request.method == 'GET':
            client_id = request.GET.get('sp_dot', "all")
            if client_id == "all":
                client_id = None

            date_start_str = request.GET.get('date_start', '')
            date_end_str = request.GET.get('date_end', '')

            filters = {}

            date_start = datetime.datetime.strptime(date_start_str, '%Y-%m-%d')  # Добавлена строка формата даты
            date_start = date_start.replace(hour=0, minute=0, second=0)  # Исправлены значения часов, минут и секунд
            date_end = datetime.datetime.strptime(date_end_str, '%Y-%m-%d')  # Добавлена строка формата даты
            date_end = date_end.replace(hour=23, minute=59, second=59)  # Исправлены значения часов, минут и секунд
            date_start_str = date_start.strftime('%Y-%m-%d %H:%M:%S')  # Преобразование обратно в строку
            date_end_str = date_end.strftime('%Y-%m-%d %H:%M:%S')  # Преобразование обратно в строку

            filters['shipment__shipmentDateFrom__range'] = (date_start_str, date_end_str)

            if client_id != None:
                filters['shipment__shippingPoint'] = request.GET.get('sp_dot', '')

            # Получите уникальные offer_id и сумму count таких же offer_id
            result = SMMItem.objects.filter(shipment__shipmentDateFrom__isnull=False, **filters).exclude(shipment__status__in=['MERCHANT_CANCELED ', 'NEW', 'PENDING', 'PENDING_CONFIRMATION' , 'CONFIRMED' , 'CONFIRMED', 'PENDING_PACKING', 'PACKED', 'PENDING_SHIPPING']).values('offerId').annotate(total_count=Sum('quantity'), total_price=Sum('finalPrice'))

            result_total = SMMItem.objects.filter(shipment__shipmentDateFrom__isnull=False, **filters).exclude(shipment__status__in=['MERCHANT_CANCELED ', 'NEW', 'PENDING', 'PENDING_CONFIRMATION' , 'CONFIRMED' , 'CONFIRMED', 'PENDING_PACKING', 'PACKED', 'PENDING_SHIPPING']).aggregate(total_count=Sum('quantity'), total_price=Sum('finalPrice'))


            data = {
                'result_total': result_total,
                'ozon_orders': list(result),
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)



def sbermegamarket_otgruzka(request):
    if check(request):
        unique_id_shops = SMMShipment.objects.values_list('shippingPoint', flat=True).distinct()

        data = {
            'unique_id_shops': unique_id_shops,
            }
        return render(request, 'marketplace/smm/smm_otgruzka.html', context=data)

    return redirect('login')


def ozon_otgruzka(request):
    if check(request):
        '''        
        oc = Ozon()
        oc.Prod_list_get()
        '''
        ozon_shops = Ozon_Settings.objects.all()
        data = {
            'ozon_shops':ozon_shops
            }
        return render(request, 'marketplace/ozon/ozon_otgruzka.html', context=data)

    return redirect('login')



def ozon_marj(request):
    if check(request):
        if request.method == 'POST':
            report_date = request.POST.get('report_date', None)
            sp_dost = request.POST.get('sp_dost', None)
            log_cheb = request.POST.get('log_cheb', None)
            client_ids = request.POST.get('client_id', None)
            client_id = Ozon_Settings.objects.get(name=client_ids).client_id
            shop_name = Ozon_Settings.objects.get(name=client_ids).name
            ozon_shops = Ozon_Settings.objects.all()
            if sp_dost == "FBO":
                ozon_orders = OzonPosting.objects.filter(in_process_at__date=report_date, client_id = client_id, delivery_method=None).exclude(status="cancelled")
                ozon_orders_delivering = OzonPosting.objects.filter(aaanalytics_data__delivery_date_end__date=report_date, client_id = client_id).exclude(status="cancelled")
            elif sp_dost == "FBS":
                ozon_orders = OzonPosting.objects.filter(in_process_at__date=report_date, client_id = client_id, delivery_method__warehouse_id__is_rfbs=False).exclude(status="cancelled")
                ozon_orders_delivering = OzonPosting.objects.filter(aaanalytics_data__delivery_date_end__date=report_date, client_id = client_id).exclude(status="cancelled")
            elif sp_dost == "rFBS":
                ozon_orders = OzonPosting.objects.filter(in_process_at__date=report_date, client_id = client_id, delivery_method__warehouse_id__is_rfbs=True).exclude(status="cancelled")
                ozon_orders_delivering = OzonPosting.objects.filter(aaanalytics_data__delivery_date_end__date=report_date, client_id = client_id).exclude(status="cancelled")
            elif sp_dost == "Все":
                ozon_orders = OzonPosting.objects.filter(in_process_at__date=report_date, client_id = client_id).exclude(status="cancelled")
                ozon_orders_delivering = OzonPosting.objects.filter(aaanalytics_data__delivery_date_end__date=report_date, client_id = client_id).exclude(status="cancelled")

            ozon_prod = ozon_orders.values(
                sku=F('financialll_data__financialll_data_product__product_id'),
                ).annotate(
                quantity_sum=Sum(Case(
                    When(financialll_data__financialll_data_product__quantity__gt=0, then='financialll_data__financialll_data_product__quantity'),
                    default=Value(1)
                )),
                price_sum=Sum('financialll_data__financialll_data_product__price'),
                ekvaring=(F('price_sum') * 0.015 ),
                del_meth=None if F('delivery_method')== None else F('delivery_method__warehouse_id__is_rfbs')  
            ).order_by('sku')

            generation_list = OzonGetProInfoMarvaV2(sku=ozon_prod, client_id=client_id, sp_dost=sp_dost)
            ozon_prod_list = list(ozon_prod)
            for op in ozon_prod_list:
                for skuinfo in generation_list:
                    if op['sku'] == skuinfo['sku']:
                        present, comission, summ, name, oofer_if = skuinfo['precent'], skuinfo['comission'], skuinfo['summ'], skuinfo['name'], skuinfo['offer_id']
                        op['sku']=oofer_if
                        op['nds_sum']=float(op['price_sum']) * 20/120
                        op['without_nds_sum']=float(op['price_sum']) - float(op['nds_sum'])
                        op['logistik_cheb_sum']=op['quantity_sum'] * int(log_cheb)
                        op['all_item_sers_sum']=summ * op['quantity_sum']
                        op['kom_sb_sum']=float(comission) * op['quantity_sum']
                        op['obj_sum_rash_mp_sum']=op['all_item_sers_sum'] + op['kom_sb_sum'] + op['ekvaring']
                        op['sum_nds_sum']=op['obj_sum_rash_mp_sum'] *20/120
                        op['obj_sum_rash_mp_bez_sum']=op['obj_sum_rash_mp_sum']-op['sum_nds_sum']
                        op['sebestoimost_sum']=0
                        op['marj_dohod']=op['without_nds_sum']-op['logistik_cheb_sum']-op['obj_sum_rash_mp_bez_sum']-op['sebestoimost_sum']
                        op['nalog_pribil']=op['marj_dohod']*20/100
                        op['chist_pribil']=op['marj_dohod']-op['nalog_pribil']
                        op['rentabelnost']=op['chist_pribil'] / op['price_sum'] *100

            

            ozon_prod_list = [{k: "{:.2f}".format(v) if isinstance(v, float) else v for k, v in d.items()} for d in ozon_prod_list]




            product_ids_and_quantities_delivering = ozon_orders_delivering.values(
                product_id=F('financialll_data__financialll_data_product__product_id')
            ).annotate(
                quantity_sum=Sum('financialll_data__financialll_data_product__quantity'),
                payout_sum=Round(Sum('financialll_data__financialll_data_product__payout'), output_field=FloatField()),
                commission_amount_sum=Round(Sum('financialll_data__financialll_data_product__commission_amount'), output_field=FloatField()),
                marketplace_service_item_deliv_to_customer_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_deliv_to_customer'), output_field=FloatField()),
                marketplace_service_item_direct_flow_trans_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_direct_flow_trans'), output_field=FloatField()),
                marketplace_service_item_dropoff_ff_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_dropoff_ff'), output_field=FloatField()),
                marketplace_service_item_dropoff_pvz_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_dropoff_pvz'), output_field=FloatField()),
                marketplace_service_item_dropoff_sc_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_dropoff_sc'), output_field=FloatField()),
                marketplace_service_item_fulfillment_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_fulfillment'), output_field=FloatField()),
                marketplace_service_item_pickup_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_pickup'), output_field=FloatField()),
                marketplace_service_item_return_after_deliv_to_customer_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_return_after_deliv_to_customer'), output_field=FloatField()),
                marketplace_service_item_return_flow_trans_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_return_flow_trans'), output_field=FloatField()),
                marketplace_service_item_return_not_deliv_to_customer_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_return_not_deliv_to_customer'), output_field=FloatField()),
                marketplace_service_item_return_part_goods_customer_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_return_part_goods_customer'), output_field=FloatField()),
            ).order_by('product_id')
            report_date = datetime.datetime.strptime(report_date, '%Y-%m-%d')
            data = {
                'product_ids_and_quantities_delivering': product_ids_and_quantities_delivering,
                'ozon_orders': ozon_orders,
                'ozon_shops': ozon_shops,
                'ozon_prod': ozon_prod_list,
                'report_date': report_date,
                'client_id': client_id,
                'sp_dost': sp_dost,
                'log_cheb': int(log_cheb),
                'shop_name': shop_name
            }
            return render(request, 'marketplace/ozon/ozon_marj.html', context=data)
        else:
            ozon_shops = Ozon_Settings.objects.all()

            shop_name= ozon_shops.first().name
            log_cheb = 50

            data = {


                'ozon_shops': ozon_shops,

                'log_cheb': int(log_cheb),
                'shop_name': shop_name
            }
            return render(request, 'marketplace/ozon/ozon_marj.html', context=data)

    return redirect('login')

def marja(request):
    if check(request) == True:
        ozon_client = Ozon()
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        ozon_transaction_list = ozon_client.GetListTransaсtion(date_from=current_date, date_to=current_date)
        

        for operation in ozon_transaction_list:
            for transaction in operation['result']['operations']:
                print(transaction)

        data = {
            'ozon_transaction_list': ozon_transaction_list
        }
        return render(request, 'marketplace/ozon/marja.html', context=data)
    else:
        return redirect('login')


smm_status_translation = {
    'MERCHANT_CANCELED': 'отмена Мерчантом',
    'NEW': 'новый заказ',
    'PENDING': 'обработка заказа со стороны Мегамаркета',
    'PENDING_CONFIRMATION ': 'обработка подтверждения со стороны Мегамаркета',
    'CONFIRMED': 'подтверждено Мерчантом',
    'PENDING_PACKING': 'обработка сообщения о комплектации со стороны Мегамаркета',
    'PACKED': 'скомплектовано Мерчантом',
    'PENDING_SHIPPING': 'обработка сообщения об отгрузке со стороны Мегамаркета',
    'SHIPPED': 'отгружено Мерчантом',
    'PACKING_EXPIRED': 'просрочка комплетации',
    'SHIPPING_EXPIRED': 'просрочка отгрузки для C&D',
    'DELIVERED': 'исполнение заказа',
    'CUSTOMER_CANCELED': 'отмена покупателем',

}    

def smm_index(request):
    if check(request)==True:
        unique_id_shops = SMMShipment.objects.values_list('shippingPoint', flat=True).distinct()
        unique_status = SMMShipment.objects.values_list('status', flat=True).distinct()
        orders = SMMShipment.objects.all()
        for order in orders:
            order.status = smm_status_translation.get(order.status, order.status)
        data = {
            'orders':orders,
            'unique_id_shops': unique_id_shops,
            'unique_status': unique_status
        }
        return render(request, 'marketplace/smm/smm_index.html', context=data)
    else:
        return redirect('login')

def sbermegamarket_orders_update_all(request):
    if check(request)==True:
        if request.method == 'GET':
            SMM_client = SberMegaMarket()
            SMM_client.GetAllOrders()
            ##SMM_client.GetShipmentInfo(token='664C2386-24D2-4140-B935-9DACA278D9CF', shipment_ids=[9588420342601])
            data = {
                'Orders': '',
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)

def sbermegamarket_orders_print(request):
    if check(request) == True:
        if request.method == 'POST':
            
            prod_list = MpProduct.objects.all()
            report_date = request.POST.get('report_date', None)
            if report_date is not None:
                report_date_datetime = datetime.datetime.strptime(report_date, '%Y-%m-%d')  # конвертируем строку в объект datetime
                report_date_plus_one_day = report_date_datetime + timedelta(days=1)  # добавляем день

        
            if report_date:
                filters = {'status__in': ['CONFIRMED', 'NEW', 'PENDING', 'PACKED'], 'shipmentDateFrom__lte': report_date_plus_one_day}
            else:
                filters = {'status__in': ['CONFIRMED', 'NEW', 'PENDING', 'PACKED']}

            order_list = SMMShipment.objects.filter(**filters)

            result_dict = defaultdict(list)

            for order in order_list:
                result_dict[order.id_shop_api].append(order.shipmentId)


            result_dict = dict(result_dict)


            smm_classes = SberMegaMarket()

            for id_shop_api, shipmentIds in result_dict.items():
                print(id_shop_api)
                print(shipmentIds)
                setting = SMM_Settings.objects.get(shop_id=id_shop_api)
                reloaded = smm_classes.GetShipmentInfo(setting.token, shipmentIds, id_shop_api)

            
            order_list = SMMShipment.objects.filter(**filters)

            product_agg = (
                SMMItem.objects.filter(shipment__in=order_list)
                .values("offerId")
                .annotate(total_quantity=Sum("quantity"))
                .order_by("offerId")
            )

            other_products = []
            chair_products = []
            pochta_orders = []
            for order in order_list:

                if order.shippingPoint == '96775' or order.shippingPoint == 96775:

                    pochta_orders.append(order)
                else:
                    for product in order.items.all():
                        try:
                            art = MpProduct.objects.get(artikul = product.offerId) 
                            if art.category.name == "Стул":
                                chair_products.append(order)
                                break
                            else:
                                other_products.append(order)
                                break
                        except:
                            other_products.append(order)


            title = f'СберМегаМаркет Списки заказов - {report_date}'
            data = {
            'title':title,
            'order_list': order_list,
            'prod_list': prod_list,
            'product_agg': product_agg,
            'other_products':other_products,
            'chair_products':chair_products,
            'pochta_orders':pochta_orders
            }

            return render(request, 'marketplace/smm/smm_spispk.html', context=data)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)

def sbermegamarket_orders_info(request, id_order):
    if check(request)==True:
        order = SMMShipment.objects.get(shipmentId=id_order)
        

        data = {

            'order': order,

        }
        return render(request, 'marketplace/smm/smm_order_info.html', context=data)
    else:
        return redirect('login')



def api_sbermegamarket_get_orders(request):
    if check(request)==True:
        if request.method == 'GET':
            date_start_str = request.GET.get('date_start', None)
            date_end_str = request.GET.get('date_end', None)
            date_end_otgr = request.GET.get('date_end_otgr', None)
            date_start_otgr = request.GET.get('date_start_otgr', None)

            shops = request.GET.get('shops')
            try:
                shops_json = json.loads(shops)

            except json.JSONDecodeError:
                print("Ошибка: строка не является допустимой JSON-строкой.")

            status = request.GET.get('status', None)
            try:
                status_json = json.loads(status)

            except json.JSONDecodeError:
                print("Ошибка: строка не является допустимой JSON-строкой.")

            orders = SMMShipment.objects.all()

            if date_start_str:
                date_start = datetime.datetime.strptime(date_start_str, '%Y-%m-%d')
                orders = orders.filter(creationDate__gte=date_start)

            if date_end_str:
                date_end = datetime.datetime.strptime(date_end_str, '%Y-%m-%d')
                orders = orders.filter(creationDate__lte=date_end)

            if date_start_otgr:
                date_start_otgr_date = datetime.datetime.strptime(date_start_otgr, '%Y-%m-%d')
                orders = orders.filter(shipment_posting_date__gte=date_start_otgr_date)

            if date_end_otgr:
                date_end_otgr_date = datetime.datetime.strptime(date_end_otgr, '%Y-%m-%d')
                orders = orders.filter(shipment_posting_date__lte=date_end_otgr_date)

            if shops_json['shop_selected']:
                orders = orders.filter(shippingPoint__in=shops_json['shop_selected'])

            if status_json['status_select']:
                orders = orders.filter(status__in=status_json['status_select'])


            orders_values = list(orders.values_list(
                'shipmentId',
                'orderCode',
                'confirmedTimeLimit',
                'packingTimeLimit',
                'shippingTimeLimit',
                'shipmentDateFrom',
                'shipmentDateTo',
                'deliveryId',
                'shipmentDateShift',
                'shipmentIsChangeable',
                'customerFullName',
                'customerAddress',
                'shippingPoint',
                'creationDate',
                'deliveryDate',
                'deliveryDateFrom',
                'deliveryDateTo',
                'deliveryMethodId',
                'depositedAmount',
                'status',
                'shipment_posting_date',
                'system_comment',
                named=True  # This will return namedtuples instead of regular tuples
            ))
            # Convert the Row objects to dictionaries
            orders_dicts = [order._asdict() for order in orders_values]

            for order_dict in orders_dicts:
                order_id = order_dict['shipmentId']  # Assuming 'id_order' is the primary key of the order
                order = SMMShipment.objects.get(shipmentId=order_id)
                items = SMMItem.objects.filter(shipment=order)  # Assuming the Item model is related to the order via ForeignKey
                txt = [f'{item.offerId}: {item.quantity}' for item in items]
                order_dict['txt'] = txt  # Add the 'txt' attribute to the dictionary

            data = {
                    'Orders': orders_dicts,
                    'status': '200'
                }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)

def api_sbermegamarket_info_update(request):
    if check(request)==True:
        if request.method == 'GET':
            comment = request.GET.get('comment', None)
            date = request.GET.get('date', None)
            order_id = request.GET.get('order_id', None)
            order = SMMShipment.objects.get(shipmentId=order_id)
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




ya_status_translation = {
    'CANCELLED': 'заказ отменен',
    'DELIVERED': 'заказ получен покупателем',
    'DELIVERY': 'заказ передан в службу доставки',
    'PICKUP': 'заказ доставлен в пункт самовывоза',
    'PROCESSING': 'заказ находится в обработке',
    'UNPAID': 'заказ оформлен, но еще не оплачен',
}    

def yandex_orders(request):
    if check(request)==True:
        unique_id_shops = YaOrder.objects.values_list('id_shop', flat=True).distinct()
        class_obj = YaMarket()
        shops = []
        for shop in unique_id_shops:
            shop_info = class_obj.GetShopInfo(shop)
            shop_info_ = {
                'id': shop,
                'name': shop_info['campaign']['business']['name']
            }
            shops.append(shop_info_)

        data = {
            'shops':shops
        }
        return render(request, 'marketplace/yamarket/ya_index.html', context=data)
    else:
        return redirect('login')


def api_yandex_get_orders(request):
    if check(request)==True:
        if request.method == 'GET':
            date_start_str = request.GET.get('date_start', None)
            date_end_str = request.GET.get('date_end', None)
            date_end_otgr = request.GET.get('date_end_otgr', None)
            date_start_otgr = request.GET.get('date_start_otgr', None)

            shops = request.GET.get('shops')
            try:
                shops_json = json.loads(shops)

            except json.JSONDecodeError:
                print("Ошибка: строка не является допустимой JSON-строкой.")

            status = request.GET.get('status', None)
            try:
                status_json = json.loads(status)

            except json.JSONDecodeError:
                print("Ошибка: строка не является допустимой JSON-строкой.")

            orders = YaOrder.objects.all()

            if date_start_str:
                date_start = datetime.datetime.strptime(date_start_str, '%Y-%m-%d')
                orders = orders.filter(creation_date__gte=date_start)

            if date_end_str:
                date_end = datetime.datetime.strptime(date_end_str, '%Y-%m-%d')
                orders = orders.filter(creation_date__lte=date_end)

            if date_start_otgr:
                date_start_otgr_date = datetime.datetime.strptime(date_start_otgr, '%Y-%m-%d')
                orders = orders.filter(shipmentDate__gte=date_start_otgr_date)

            if date_end_otgr:
                date_end_otgr_date = datetime.datetime.strptime(date_end_otgr, '%Y-%m-%d')
                orders = orders.filter(shipmentDate__lte=date_end_otgr_date)

            if shops_json['shop_selected']:
                orders = orders.filter(id_shop__in=shops_json['shop_selected'])

            if status_json['status_select']:
                orders = orders.filter(status__in=status_json['status_select'])


            orders_values = list(orders.values_list(
                'id_order',
                'status',
                'substatus',
                'creation_date',
                'items_total',
                'total',
                'delivery_total',
                'subsidy_total',
                'total_with_subsidy',
                'buyer_items_total',
                'buyer_total',
                'buyer_items_total_before_discount',
                'buyer_total_before_discount',
                'payment_type',
                'payment_method',
                'fake',
                'id_shop',
                'shipmentDate',
                named=True  # This will return namedtuples instead of regular tuples
            ))
            # Convert the Row objects to dictionaries
            orders_dicts = [order._asdict() for order in orders_values]

            for order_dict in orders_dicts:
                order_id = order_dict['id_order']  # Assuming 'id_order' is the primary key of the order
                order = YaOrder.objects.get(id_order=order_id)
                items = YaItem.objects.filter(ya_order=order)  # Assuming the Item model is related to the order via ForeignKey
                txt = [f'{item.offer_id}: {item.count}' for item in items]
                order_dict['txt'] = txt  # Add the 'txt' attribute to the dictionary

            data = {
                    'Orders': orders_dicts,
                    'status': '200'
                }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)



def yandex_orders_update_all(request):
    if check(request)==True:
        if request.method == 'GET':
            ya_class = YaMarket()
            company_list = ya_class.GetCompany()

            for company in company_list['campaigns']:
                ya_class.GetOrders(campaignId=company['id'])

            data = {
                'Orders': '',
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)

def yandex_orders_print(request):
    if check(request) == True:
        if request.method == 'POST':
            prod_list = MpProduct.objects.all()
            report_date = request.POST.get('report_date', None)
            if report_date is not None:
                report_date_datetime = datetime.datetime.strptime(report_date, '%Y-%m-%d')  # конвертируем строку в объект datetime
                report_date_plus_one_day = report_date_datetime  # добавляем день

            if report_date:
                filters = {'status': 'PROCESSING', 'shipmentDate__lte': report_date_plus_one_day}
            else:
                filters = {'status': 'PROCESSING'}

            # Load all order_list with related items
            order_list = YaOrder.objects.filter(**filters).order_by('shipmentDate').exclude(substatus='SHIPPED')


            other_products = []
            chair_products = []
            for order in order_list:
                for product in order.items.all():
                    try:
                        art = MpProduct.objects.get(artikul = product.offer_id) 
                        if art.category.name == "Стул":
                            chair_products.append(order)
                            break
                        else:
                            other_products.append(order)
                            break
                    except:
                        other_products.append(order)


            unique_items = order_list.values('items__offer_id', 'items__count').annotate(count=Count('items__offer_id')).order_by()

            unique_items_list = list(unique_items)

            title = f'Яндекс.Маркет Списки заказов - {report_date}'
            data = {
            'type': 'Яндекс.Маркет',
            'title': title,
            'order_list': order_list,
            'other_products': other_products,
            'chair_products': chair_products,      
            'unique_items_list':unique_items_list      

            }

            return render(request, 'marketplace/yamarket/yandex_spispk.html', context=data)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)

def yandex_orders_info(request, id_order):
    if check(request)==True:
        order = YaOrder.objects.get(id_order=id_order)
        

        data = {

            'order': order,

        }
        return render(request, 'marketplace/yamarket/ya_order_info.html', context=data)
    else:
        return redirect('login')


def api_yandex_info_update(request):
    if check(request)==True:
        if request.method == 'GET':
            comment = request.GET.get('comment', None)
            date = request.GET.get('date', None)
            order_id = request.GET.get('order_id', None)
            order = YaOrder.objects.get(id_order=order_id)
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


def api_mp_products_add(request):
    if check(request)==True:
        if request.method == 'GET':
            # Получаем данные из GET-запроса
            art = request.GET.get('art', '')
            type_pos = request.GET.get('type_pos', '')
            kokon = request.GET.get('kokon', '')
            color_kokon = request.GET.get('color_kokon', '')
            pletenie = request.GET.get('pletenie', '')
            color_pletenie = request.GET.get('color_pletenie', '')
            duga = request.GET.get('duga', '')
            color_duga = request.GET.get('color_duga', '')
            osnovanie = request.GET.get('osnovanie', '')
            color_osnovanie = request.GET.get('color_osnovanie', '')
            forma_pud = request.GET.get('forma_pud', '')
            tip_tkan = request.GET.get('tip_tkan', '')
            color_tkan = request.GET.get('color_tkan', '')
            any_val = request.GET.get('any', '')
            color_any = request.GET.get('color_any', '')
            mebel = request.GET.get('mebel', '')
            color_mebel = request.GET.get('color_mebel', '')

            # Проверяем, существует ли товар с данным 'artikul'
            if MpProduct.objects.filter(artikul=art).exists():
                return JsonResponse({'status': 403})  # Ошибка - товар уже существует

            # Создаем новую модель MpProduct, пропуская пустые значения
            new_product = MpProduct(
                artikul=art if art else None,
                type=type_pos if type_pos else None,
                kokon=kokon if kokon else None,
                svet_kokon=color_kokon if color_kokon else None,
                pletenie=pletenie if pletenie else None,
                cvet_pletenie=color_pletenie if color_pletenie else None,
                duga=duga if duga else None,
                cvet_duga=color_duga if color_duga else None,
                osnovanie=osnovanie if osnovanie else None,
                cvet_osnovanie=color_osnovanie if color_osnovanie else None,
                forma_podishki=forma_pud if forma_pud else None,
                tip_tkani=tip_tkan if tip_tkan else None,
                cvet_tkani=color_tkan if color_tkan else None,
                any=any_val if any_val else None,
                cvet_any=color_any if color_any else None,
                mebel=mebel if mebel else None,
                cvet_mebel=color_mebel if color_mebel else None
            )
            new_product.save()

            return JsonResponse({'status': 200})  # Успешное создание модели

        return JsonResponse({'status': 400})  # Неизвестная ошибка
    else:
        return JsonResponse({'status': '405'}, status=405)
    
def api_mp_products_get(request):
    if check(request)==True:
        if request.method == 'GET':
            products = MpProduct.objects.all()
            product_list = []
            for product in products:
                characteristics = {
                    'kokon': product.kokon,
                    'svet_kokon': product.svet_kokon,
                    'pletenie': product.pletenie,
                    'cvet_pletenie': product.cvet_pletenie,
                    'duga': product.duga,
                    'cvet_duga': product.cvet_duga,
                    'osnovanie': product.osnovanie,
                    'cvet_osnovanie': product.cvet_osnovanie,
                    'forma_podishki': product.forma_podishki,
                    'tip_tkani': product.tip_tkani,
                    'cvet_tkani': product.cvet_tkani,
                    'mebel': product.mebel,
                    'cvet_mebel': product.cvet_mebel,
                    'any': product.any,
                    'cvet_any': product.cvet_any,
                }
                product_data = {
                    'artikul': product.artikul,
                    'type': product.type,
                    'characteristics': characteristics
                }
                product_list.append(product_data)

            return JsonResponse({'products': product_list})
        return JsonResponse({'status': 400})  # Неизвестная ошибка
    else:
        return JsonResponse({'status': '405'}, status=405)
    

def ozon_get_dost(request):
    if check(request)==True:
        if request.method == 'GET':
            sp_dost_main = request.GET.get('sp_dost_main', '')
            Istochniki = list(OzonDeliveryMethod.objects.all().values_list('id','name', 'warehouse', 'tpl_provider'))
            tpl_providers = OzonDeliveryMethod.objects.all().values_list('tpl_provider', flat=True)
            unique_tpl_providers = list(set(tpl_providers))
            tpl_provider_filter = sp_dost_main  # замените "your_value" на значение 'tpl_provider', которое вы хотите использовать для фильтрации

            warehouses = OzonDeliveryMethod.objects.filter(tpl_provider=tpl_provider_filter).values_list('warehouse', flat=True)
            unique_warehouses = list(set(warehouses))
            data = {
                'Istochniki': Istochniki,
                'unique_tpl_provider_values':unique_tpl_providers,
                'unique_warehouses':unique_warehouses,
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)
    

def api_mp_finance_get(request):
    if check(request)==True:
        if request.method == 'GET':
            OzonData = Ozon()
            start = request.GET.get('start', '')
            end = request.GET.get('end', '')
            total_am = OzonData.TotalTranz(date_from=start, date_to=end)
            data = {
                'total_am': total_am,
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)
    

def ozon_fbs_ord(request, Date_End, Status, SpDostMain):
    if check(request) == True:
        if request.method == 'GET':
            SpDostMain = urllib.parse.unquote(SpDostMain)
            prod_list = MpProduct.objects.all()

            # Преобразование строковой даты в datetime
            Date_End = datetime.datetime.strptime(Date_End, '%Y-%m-%d') + datetime.timedelta(1)

            # Создание словаря с базовыми фильтрами
            filters = {'shipment_posting_date__lte': Date_End}

            if SpDostMain != "all":
                filters.update({'delivery_method__tpl_provider': SpDostMain})
            
            # Если Status не равно "all", добавьте его в фильтры
            if Status != "all":
                filters.update({'status': Status})

            order_list = OzonPosting.objects.select_related(
                'delivery_method'
            ).prefetch_related(
                'products',
            ).filter(
                **filters
            ).order_by('shipment_posting_date').exclude(status="cancelled", delivery_method=None)


            other_products = []
            chair_products = []
            for order in order_list:
                financial_data = Ozon_FinancialData.objects.get(ozon_posting=order)
                products = financial_data.financialll_data_product.all()

                for i in products:
                    try:
                        get = Ozon_ProductList.objects.get(product_id=i.product_id)
                        try:
                            product = MpProduct.objects.get(artikul=get.offer_id)
                            if product.category.name == "Стул":
                                chair_products.append(order)
                                break
                            else:
                                other_products.append(order)
                        except ObjectDoesNotExist:
                            other_products.append(order)
                    except:
                        other_products.append(order)

            
            product_agg = order_list.values('products__offer_id').annotate(total_quantity=Sum('products__quantity')).order_by('-products__offer_id')




            grouped_orders = {}
            for order in other_products:
                if order.delivery_method.tpl_provider not in grouped_orders:
                    grouped_orders[order.delivery_method.tpl_provider] = []
                grouped_orders[order.delivery_method.tpl_provider].append(order)


            grouped_orders_chair = {}
            for order in chair_products:
                if order.delivery_method.tpl_provider not in grouped_orders_chair:
                    grouped_orders_chair[order.delivery_method.tpl_provider] = []
                grouped_orders_chair[order.delivery_method.tpl_provider].append(order)

            for pg in product_agg:
                try:
                    obj = MpProduct.objects.get(artikul=pg['products__offer_id'])
                    obj_dict = vars(obj)
                    pg.update(obj_dict)
                except MpProduct.DoesNotExist:
                    continue

            Date_End = Date_End - datetime.timedelta(1)
            Date_End = Date_End.strftime('%d.%m.%Y')
            
            Status = status_mapping.get(Status)
            data = {
                'type': f'{Status} - {Date_End}',
                'order_list': order_list,
                'odrers_by_del_meth': grouped_orders,
                'prod_list': prod_list,  # нужно обновить, если `prod_list` используется в контексте (не указан в исходной функции)
                'product_agg': product_agg,
                'status': '200',
                'grouped_orders_chair': grouped_orders_chair
                
            }

            return render(request, 'marketplace/ozon/spisok_fbs.html', context=data)

        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)


def api_ozon_info_update(request):
    if check(request)==True:
        if request.method == 'GET':
            comment = request.GET.get('comment', None)
            date = request.GET.get('date', None)
            order_id = request.GET.get('order_id', None)
            order = OzonPosting.objects.get(posting_number=order_id)
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


def ozon_get_status(request):
    if check(request)==True:
        if request.method == 'GET':
            Istochniki = list(Ozon_Status.objects.all().values_list('id','name','ru_name'))
            data = {
                'Istochniki': Istochniki,
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)

pochta_list = {
"add-to-mmo": "Многоместное отправление",
"address-changed": "Адрес получателя скорректирован",
"address-type-from": "Тип адреса",
"address-type-to": "Тип адреса",
"area-from": "Район отправителя",
"area-to": "Район",
"arrival-date": "Дата прибытия отправления в место вручения",
"avia-rate": "Авиа-сбор без НДС (для совместимости)",
"avia-rate-with-vat": "Авиа-сбор с НДС",
"avia-rate-wo-vat": "Авиа-сбор без НДС",
"barcode": "ШПИ",
"batch-category": "Категория партии",
"batch-name": "Внешний идентификатор партии заказа",
"batch-status": "Статус партии",
"bk-hash": "Хэш-код",
"branch-name": "Идентификатор подразделения",
"building-from": "Часть здания: Строение отправителя",
"building-to": "Часть здания: Строение",
"completeness-checking": "Признак услуги проверки комплектности",
"completeness-checking-rate-with-vat": "Надбавка за 'Проверку комплектности' с НДС",
"completeness-checking-rate-wo-vat": "Надбавка за 'Проверку комплектности' без НДС",
"compulsory-payment": "К оплате с получателя (копейки)",
"contents-checking-rate-with-vat": "Надбавка за 'Проверку вложений' с НДС",
"contents-checking-rate-wo-vat": "Надбавка за 'Проверку вложений' без НДС",
"corpus-from": "Часть здания: Корпус отправителя",
"corpus-to": "Часть здания: Корпус",
"customs-declaration": "Таможенная декларация",
"certificate-number": "Сертификаты, сопровождающие отправление",
"comments": "Комментарии",
"currency": "Код валюты",
"customs-code": "Код таможенного органа",
"customs-comments": "Комментарии таможенного органа",
"customs-decision": "Решение таможенного органа",
"customs-entries": "Список вложений",
"amount": "Количество",
"country-code": "Код страны происхождения",
"description": "Наименование товара",
"entry-number": "Порядковый номер",
"tnved-code": "Код ТНВЭД",
"trademark": "Торговая марка",
"value": "Цена за единицу товара в копейках (вкл. НДС)",
"weight": "Вес товара (в граммах)",
"decision-date": "Дата решения таможенного органа",
"decision-description": "Описание решения таможенного органа",
"entries-type": "Категория вложения",
"fts-error": "Ошибка декларирования",
"invoice-number": "Счет (номер счета-фактуры)",
"ioss-code": "Регистрационный код продавца",
"license-number": "Лицензии, сопровождающие отправление",
"recom-description": "Описание рекомендации таможенного органа",
"registration-date": "Дата регистрации документа таможенным органом",
"status": "Статус декларации в процессе электронного декларирования",
"with-certificate": "Приложенные документы: сертификат",
"with-invoice": "Приложенные документы: счет-фактура",
"with-license": "Приложенные документы: лицензия",
"declaration-status": "Результат электронного декларирования",
"delivery-time": "Время доставки",
"max-days": "Максимальное время доставки (дни)",
"min-days": "Минимальное время доставки (дни)",
"delivery-with-cod": "Признак оплаты при получении",
"dimension": "Линейные размеры",
"height": "Линейная высота (сантиметры)",
"length": "Линейная длина (сантиметры)",
"width": "Линейная ширина (сантиметры)",
"dimension-type": "Типоразмер",
"easy-return-rate-with-vat": "Сбор за 'Лёгкий возврат' с НДС",
"easy-return-rate-wo-vat": "Сбор за 'Лёгкий возврат' без НДС",
"ecom-data": 'Данные ЕКОМ',
"delivery-point-index": "Идентификатор пункта выдачи",
"delivery-point-type": "Тип пункта выдачи",
"identity-methods": "Методы идентификации личности",
"services": "Коды видов сервиса",
"electronic-notification-history": "История электронной нотификации",
"items": "Список вложений",
"has-external-resource": "Признак наличия внешнего ресурса",
"is-download": "Признак скачивался ли ЭУВ клиентом",
"oper-attr": "Атрибут операции",
"oper-date": "Дата и время операции",
"oper-type": "Тип операции",
"envelope-type": "Тип конверта - ГОСТ Р 51506-99",
"fiscal-data": "Фискальные данные",
"customer-email": "Адрес электронной почты плательщика",
"customer-inn": "ИНН юридического лица покупателя",
"customer-name": "Наименование юридического лица покупателя",
"customer-phone": "Телефон плательщика",
"fiscal-payments": "Средства, использованные при оплате",
"payment-amount": "Сумма оплаты платежным средством,(копейки)",
"payment-kind": "Вид платежного средства",
"payment-type": "Тип платежного средства",
"fragile-rate-with-vat": "Надбавка за отметку 'Осторожно/Хрупкое'",
"fragile-rate-wo-vat": "Надбавка за отметку 'Осторожно/Хрупкое' без НДС",
"functionality-checking-rate-with-vat": "Надбавка за 'Проверку вложений с проверкой работоспособности' с НДС",
"functionality-checking-rate-wo-vat": "Надбавка за 'Проверку вложений с проверкой работоспособности' без НДС",
"given-name": "Имя получателя",
"goods": "Товарное вложение РПО",
"items": "Список вложений",
"category-feature": "Категория товара",
"code": "Код (маркировка) товара",
"country-code": "Код страны происхождения",
"customs-declaration-number": "Номер таможенной декларации",
"description": "Наименование товара",
"excise": "Акциз (копейки)",
"goods-type": "Тип вложения",
"id": "Номер товара в списке вложений",
"insr-value": "Объявленная ценность (копейки)",
"item-number": "Номенклатура (артикул) товара",
"lineattr": "Признак предмета расчета",
"payattr": "Признак способа расчета",
"quantity": "Количество товара",
"returned": "Статус возврата, вложения(ЕКОМ)",
"supplier-inn": "ИНН поставщика товара",
"supplier-name": "Наименование поставщика товара",
"supplier-phone": "Телефон поставщика товара",
"value": "Цена за единицу товара в копейках (вкл. НДС)",
"vat-rate": "Ставка НДС: Без НДС(-1), 0, 10, 110, 20, 120",
"weight": "Вес товара (в граммах)",
"ground-rate": "Сбор за доставку наземно без НДС (для совместимости)",
"ground-rate-with-vat": "Сбор за доставку наземно с НДС",
"ground-rate-wo-vat": "Сбор за доставку наземно без НДС",
"group-name": "Наименование группы",
"hotel-from": "Название гостиницы отправителя",
"hotel-to": "Название гостиницы",
"house-from": "Часть адреса: Номер здания отправителя",
"house-to": "Часть адреса: Номер здания",
"human-operation-name": "Наименование операции",
"hyper-local-status": "Статус по гиперлокальной доставке. См. Статус по гиперлокальной доставке",
"id": "Номер товара в списке вложений",
"in-mmo": "Отправление в составе ММО",
"index-from": "Почтовый индекс отправителя",
"index-to": "Почтовый индекс",
"inner-num": "Дополнительный идентификатор отправления",
"insr-rate": "Плата за ОЦ без НДС (для совместимости)",
"insr-rate-with-vat": "Плата за ОЦ с НДС",
"insr-rate-wo-vat": "Плата за ОЦ без НДС",
"insr-value": "Объявленная ценность (копейки)",
"inventory-rate-with-vat": "Надбавка за 'Опись вложения' с НДС",
"inventory-rate-wo-vat": "Надбавка за 'Опись вложения' без НДС",
"is-deleted": "Заказ удален?",
"last-oper-attr": "Атрибут последней операции из трекинга",
"last-oper-type": "Тип последней операции из трекинга",
"legal-hid": "Почта ID HID юридического лица",
"letter-from": "Часть здания: Литера отправителя",
"letter-to": "Часть здания: Литера",
"linked-barcode": "ШПИ связанного отправления",
"location-from": "Микрорайон отправителя",
"location-to": "Микрорайон",
"mail-category": "Категория РПО",
"mail-direct": "Код страны",
"mail-rank": "Код разряда почтового отправления",
"mail-type": "Вид РПО",
"mass": "Вес РПО (в граммах)",
"mass-rate": "Почтовый сбор без НДС (для совместимости)",
"mass-rate-with-vat": "Почтовый сбор с НДС",
"mass-rate-wo-vat": "Почтовый сбор без НДС",
"middle-name": "Отчество получателя",
"mpo-declaration": "Данные таможенной декларации в формате XML",
"notice-payment-method": "Способ оплаты",
"notice-rate-with-vat": "Надбавка за уведомление о вручении с НДС",
"notice-rate-wo-vat": "Надбавка за уведомление о вручении без НДС",
"num-address-type-from": "Номер для а/я, войсковая часть, войсковая часть ЮЯ, полевая почта отправителя",
"num-address-type-to": "Номер для а/я, войсковая часть, войсковая часть ЮЯ, полевая почта",
"office-from": "Часть здания: Офис отправителя",
"office-to": "Часть здания: Офис",
"online-payment-mark": "Знак онлайн оплаты",
"index-oper": "Индекс ОПС приёма",
"online-payment-mark-id": "Уникальный идентификатор ЗОО",
"value": "Цена за единицу товара в копейках (вкл. НДС)",
"order-num": "Номер заказа. Внешний идентификатор заказа, который формируется отправителем",
"oversize-rate-with-vat": "Надбавка за негабарит при весе более 10кг с НДС",
"oversize-rate-wo-vat": "Надбавка за негабарит при весе более 10кг без НДС",
"partial-redemption-rate-with-vat": "Надбавка за 'Частичный выкуп' с НДС",
"partial-redemption-rate-wo-vat": "Надбавка за 'Частичный выкуп' без НДС",
"payment": "Сумма наложенного платежа (копейки)",
"payment-method": "Способ оплаты. См. Способ оплаты",
"place-from": "Населенный пункт отправителя",
"place-to": "Населенный пункт",
"pochtaid-hid": "Почта ID HID",
"postmarks": "Коды отметок внутренних и международных отправлений",
"postoffice-code": "Индекс места приема",
"pre-postal-preparation": "Отметка 'Предпостовая подготовка'",
"pre-postal-preparation-rate-with-vat": "Надбавка за 'Предпочтовая подготовка' с НДС",
"pre-postal-preparation-rate-wo-vat": "Надбавка за 'Предпочтовая подготовка' без НДС",
"prepaid-amount": "Сумма частичной предоплаты",
"raw-address": "Необработанный адрес получателя",
"recipient-name": "Наименование получателя одной строкой (ФИО, наименование организации)",
"region-from": "Область, регион отправителя",
"region-to": "Область, регион",
"renewal-shelf-life": "Признак подачи заявления на продление срока хранения",
"returned-partial": "Признак частичного возврата",
"room-from": "Часть здания: Номер помещения отправителя",
"room-to": "Часть здания: Номер помещения",
"sender-comment": "Комментарий отправитяля к ЭУВ",
"sender-name": "Наименование отправителя одной строкой (ФИО, наименование организации)",
"shelf-life-days": "Срок хранения отправления от 15 до 60 дней",
"slash-from": "Часть здания: Дробь отправителя",
"slash-to": "Часть здания: Дробь",
"sms-notice-recipient": "Признак услуги SMS уведомления",
"sms-notice-recipient-rate-with-vat": "Надбавка за 'Пакет смс получателю' с НДС",
"sms-notice-recipient-rate-wo-vat": "Надбавка за 'Пакет смс получателю' без НДС",
"str-index-to": "Почтовый индекс (буквенно-цифровой)",
"street-from": "Часть адреса: Улица отправителя",
"street-to": "Часть адреса: Улица",
"surname": "Фамилия получателя",
"tel-address": "Телефон получателя (может быть обязательным для некоторых типов отправлений)",
"tel-address-from": "Телефон отправителя",
"total-rate-wo-vat": "Плата всего без НДС (коп)",
"total-vat": "Всего НДС (коп)",
"track-by-group": "Услуга 'Отслеживание группой'",
"transport-type": "Вид транспортировки",
"version": "Версия заказа",
"vladenie-from": "Часть здания: Владение отправителя",
"vladenie-to": "Часть здания: Владение",
"vsd-rate-with-vat": "Надбавка за 'Возврат сопроводительных документов' с НДС",
"vsd-rate-wo-vat": "Надбавка за 'Возврат сопроводительных документов' без НДС",
"with-fitting-rate-with-vat": "Надбавка за 'Проверку вложений с примеркой' с НДС",
"with-fitting-rate-wo-vat": "Надбавка за 'Проверку вложений с примеркой' без НДС",
}



def translate_keys(obj, translation_dict):
    if isinstance(obj, dict):
        return {
            translation_dict.get(k, k): translate_keys(v, translation_dict)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [translate_keys(elem, translation_dict) for elem in obj]
    else:
        return obj
    
def order_info(request, posting_number):
    if check(request)==True:
        order = OzonPosting.objects.get(posting_number=posting_number)
        client_id = order.client_id
        prod_list = MpProduct.objects.all()
        status_translation = status_mapping.get(order.status, 'Unknown')
        pochta_info = ''
        cdek_info = ''
        tpl_provider = order.delivery_method.tpl_provider
        
        if order.tracking_number.startswith('E'):
            PochtaClient = PochtaRussia()
            pochta_info = PochtaClient.search_by_track_number(track_number=str(order.tracking_number))
            pochta_info = translate_keys(pochta_info, pochta_list)

        if tpl_provider == 'СДЭК' and order.tracking_number:
            try:
                CDEK_client = CDEK()
                cdek_info = CDEK_client.get_order_info(order.tracking_number)
            except:
                CDEK_client = CDEK_Roznica()
                cdek_info = CDEK_client.get_order_info(order.tracking_number)
            cdek_info['entity']['statuses'].reverse()
            for status in cdek_info['entity']['statuses']:
                date_time_str = status['date_time']
                # Удалить символ '+0000', если он есть, чтобы не возникало ошибки
                date_time_str = date_time_str.replace('+0000', '')
                # Теперь пытаемся преобразовать строку в объект datetime
                try:
                    date_time_obj = datetime.datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S")
                    formatted_date_time = date_time_obj.strftime("%m.%d.%Y %H:%M:%S")
                    status['date_time'] = formatted_date_time
                except ValueError:
                    print(f"Не удалось преобразовать строку: {date_time_str}")
            

        data = {
            'client_id': client_id,
            'order': order,
            'prod_list': prod_list,
            'status_translation': status_translation,
            'pochta_info':pochta_info,
            'cdek_info':cdek_info
        }
        return render(request, 'marketplace/ozon/order_info.html', context=data)
    else:
        return redirect('login')
    
def Uopdd():
    MpProduct.objects.all().delete()
    ProductCharacteristic.objects.all().delete()
    Category.objects.all().delete()
    Characteristic.objects.all().delete()
    with open('D:\STULER_CRM\Файлы\csv_Артиклы_МП.csv', 'r', encoding='utf-8') as f:
        data = csv.DictReader(f, delimiter=';')
        for row in data:
            artikul = row['\ufeffАртикул']
            category_name = row['Тип товара']
            category, _ = Category.objects.get_or_create(name=category_name)

            kol = row.get('Количество стульев', 1) or 1

            product = MpProduct.objects.create(
                artikul=artikul,
                category=category,
                kol=kol,
            )

            # Создание и связывание характеристик товара
            for column, value in row.items():
                if column not in ['\ufeffАртикул', 'Тип товара'] and value:
                    characteristic, _ = Characteristic.objects.get_or_create(name=column)
                    ProductCharacteristic.objects.create(product=product, characteristic=characteristic, value=value)

            product.save()


    return

def ozon_get_orders(request):
    if check(request)==True:
        if request.method == 'GET':
            OzonData = Ozon()
            date = datetime.datetime.today()
            from_date= date - datetime.timedelta(21)
            OzonData.GetOrders(date_from=from_date.strftime('%Y-%m-%d'), date_to=date.strftime('%Y-%m-%d'))
            print(f"date from: { from_date } \n date to: { date }")
            data = {
                'Orders': '',
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)

status_mapping = {
    'acceptance_in_progress': 'Идёт приёмка',
    'arbitration': 'Арбитраж',
    'awaiting_approve': 'Ожидает подтверждения',
    'awaiting_deliver': 'Ожидает отгрузки',
    'awaiting_packaging': 'Ожидает упаковки',
    'awaiting_registration': 'Ожидает регистрации',
    'awaiting_verification': 'Создано',
    'cancelled': 'Отменено',
    'cancelled_from_split_pending': 'Отменено',
    'client_arbitration': 'Елиентский арбитраж доставки',
    'delivered': 'Доставлено',
    'delivering': 'Доставляется',
    'driver_pickup': 'У водителя',
    'not_accepted': 'Не принят на сортировочном центре',
    'sent_by_seller': 'Отправлено продавцом',
}    


def ozon_gets_orders_table(request):
    if check(request)==True:
        if request.method == 'GET':
            sp_dot = request.GET.get('sp_dot', None)
            status = request.GET.get('status', None)
            date_start = request.GET.get('date_start', None)
            date_end = request.GET.get('date_end', None)
            date_start_otrg = request.GET.get('date_start_otrg', None)
            date_end_otrg = request.GET.get('date_end_otrg', None)

            # Prepare date filters
            date_filters = {}
            if date_start and date_end:
                date_end = datetime.datetime.strptime(date_end, '%Y-%m-%d') + datetime.timedelta(days=1)
                date_filters['in_process_at__range'] = [date_start, date_end]
            if date_start_otrg and date_end_otrg:
                date_end_otrg = datetime.datetime.strptime(date_end_otrg, '%Y-%m-%d') + datetime.timedelta(days=1)
                date_filters['shipment_date__range'] = [date_start_otrg, date_end_otrg]

            # Prepare status and delivery method filters
            status_filter = {}
            if sp_dot and sp_dot != "all":
                del_meth = int(sp_dot)
                status_filter['delivery_method__id'] = del_meth
            if status and status != "all":
                status_filter['status'] = status

            # Combine filters
            filters = Q(**date_filters) & Q(**status_filter)

            # Perform query
            OzonPostings = OzonPosting.objects.filter(filters).values_list(
                'posting_number', 'order_id', 'order_number', 'status', 'delivery_method',
                'tracking_number', 'tpl_integration_type', 'in_process_at', 'shipment_date',
                'delivering_date', 'cancellation', 'customer__name', 'products', 'substatus',
                'mandatory_mark', 'parent_posting_number', 'prr_option', 'multi_box_qty',
                'is_multibox', 'substatus', 'prr_option', 'is_express', 'addressee',
                'barcodes', 'analytics_data', 'available_actions', 'requirements'
            ).order_by('-in_process_at')

            formatted_postings = []
            for posting in OzonPostings:
                formatted_posting = list(posting)
                formatted_posting[7] = posting[7].strftime('%d.%m.%Y') if posting[7] else None  # in_process_at
                formatted_posting[8] = posting[8].strftime('%d.%m.%Y') if posting[8] else None  # shipment_date
                formatted_posting[9] = posting[9].strftime('%d.%m.%Y') if posting[9] else None  # delivering_date
                id = posting[0]
                order = OzonPosting.objects.get(posting_number=id)
                financial_data = Ozon_FinancialData.objects.get(ozon_posting=order)
                products = financial_data.financialll_data_product.all()
                txt = ""
                is_first_iteration = True

                for i in products:
                    try:
                        get = Ozon_ProductList.objects.get(product_id=i.product_id)
                        try:
                            product = MpProduct.objects.get(artikul=get.offer_id)
                            if not is_first_iteration:
                                txt += ', '
                            txt += product.artikul
                            is_first_iteration = False
                        except ObjectDoesNotExist:
                            if not is_first_iteration:
                                txt += ', '
                            txt += 'Ошибка 2'
                            is_first_iteration = False
                    except:
                        if not is_first_iteration:
                            txt += ', '
                        txt += 'Ошибка 1'
                        is_first_iteration = False
                        
                formatted_postings.append(formatted_posting)
                formatted_posting.append(txt)

            data = {
                'Orders': formatted_postings,
                'status': '200'
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'status': '403'}, status=400)
    else:
        return JsonResponse({'status': '405'}, status=405)

def parse_date_or_datetime(date_string):
    for fmt in ['%d-%m-%Y %H:%M:%S', '%d-%m-%Y']:
        try:
            return datetime.datetime.strptime(date_string, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_new_value(product):
    del_meth_mapping = {
            None: 'FBO',
            True: 'FBS',
            False: 'rFBS'
        }       
    return del_meth_mapping.get(product['del_meth'], 'Неизвестно')


def get_ozon_sku_mine_system(product):
    try:
        get = Ozon_ProductList.objects.get(product_id=product)
        try:
            product = MpProduct.objects.get(artikul=get.offer_id)
            if product.category.name == "Стул":
                
                return product
            if  product.category.name != "Стул":
                return product
        except:
            return False
    except:
        return False
                                    


class generate_csv_marj_ozon(View):
    def get(self, request):

        end_date = request.GET.get('another_date')
        start_date = request.GET.get('report_date', None)
        sp_dost = request.GET.get('sp_dost', None)
        log_cheb = request.GET.get('log_cheb', None)
        client_ids = request.GET.get('client_id', None)

        # Преобразование строк в объекты datetime
        start_date = datetime.datetime.strptime(request.GET.get('report_date'), '%Y-%m-%d')
        end_date = datetime.datetime.strptime(request.GET.get('another_date'), '%Y-%m-%d')

        # Проверка, что дата начала меньше даты конца
        if start_date > end_date:
            raise ValueError("Дата начала должна быть меньше даты конца")

        # Заголовки для нашего CSV-файла
        fieldnames = [
                'data',
                'ТП',
                'sku',
                'name',
                'Количество купленных сегодня',
                'Сумма Купленных сегодня',
                'Сумма НДС',
                'Сумма без НДС',
                'Сумма Экваринга',
                'Логистика Чебоксары',
                'Логистика МП',
                'Комиссия МП',
                'Общая сумма расхода маркетплейса с НДС',
                'Сумма НДС',
                'Общая сумма расхода маркетплейса без НДС',
                'Себестоимость',
                'Маржинальный доход',
                'Налог на прибыль',
                'Чистая прибыль',
                'Рентабельность по чистой прибыли в %',
            ]
        
        data = []

        data.append(fieldnames)  # Добавим заголовки в наш список data




        # Цикл по каждой дате в диапазоне
        current_date = start_date
        while current_date <= end_date:

            report_date = current_date
            client_id = Ozon_Settings.objects.get(client_id=client_ids).client_id
            shop_name = Ozon_Settings.objects.get(client_id=client_ids).name
            ozon_shops = Ozon_Settings.objects.all()
            if sp_dost == "FBO":
                ozon_orders = OzonPosting.objects.filter(in_process_at__date=report_date, client_id = client_id, delivery_method=None).exclude(status="cancelled")
                ozon_orders_delivering = OzonPosting.objects.filter(aaanalytics_data__delivery_date_end__date=report_date, client_id = client_id).exclude(status="cancelled")
            elif sp_dost == "FBS":
                ozon_orders = OzonPosting.objects.filter(in_process_at__date=report_date, client_id = client_id, delivery_method__warehouse_id__is_rfbs=False).exclude(status="cancelled")
                ozon_orders_delivering = OzonPosting.objects.filter(aaanalytics_data__delivery_date_end__date=report_date, client_id = client_id).exclude(status="cancelled")
            elif sp_dost == "rFBS":
                ozon_orders = OzonPosting.objects.filter(in_process_at__date=report_date, client_id = client_id, delivery_method__warehouse_id__is_rfbs=True).exclude(status="cancelled")
                ozon_orders_delivering = OzonPosting.objects.filter(aaanalytics_data__delivery_date_end__date=report_date, client_id = client_id).exclude(status="cancelled")
            elif sp_dost == "all":
                ozon_orders = OzonPosting.objects.filter(in_process_at__date=report_date, client_id = client_id).exclude(status="cancelled")
                ozon_orders_delivering = OzonPosting.objects.filter(aaanalytics_data__delivery_date_end__date=report_date, client_id = client_id).exclude(status="cancelled")

            ozon_prod = ozon_orders.values(
                    sku=F('financialll_data__financialll_data_product__product_id'),
                    ).annotate(
                    quantity_sum=Sum(Case(
                        When(financialll_data__financialll_data_product__quantity__gt=0, then='financialll_data__financialll_data_product__quantity'),
                        default=Value(1)
                    )),
                    price_sum=Sum('financialll_data__financialll_data_product__price'),
                    ekvaring=(F('price_sum') * 0.015 ),
                    del_meth=None if F('delivery_method')== None else F('delivery_method__warehouse_id__is_rfbs')  
                ).order_by('sku')

            generation_list = OzonGetProInfoMarvaV2(sku=ozon_prod, client_id=client_id, sp_dost=sp_dost)
            ozon_prod_list = list(ozon_prod)
            for op in ozon_prod_list:
                for skuinfo in generation_list:
                    if op['sku'] == skuinfo['sku']:

                        present, comission, summ, name, oofer_if = skuinfo['precent'], skuinfo['comission'], skuinfo['summ'], skuinfo['name'], skuinfo['offer_id']
                        op['sku']=oofer_if
                        op['nds_sum']=float(op['price_sum']) * 20/120
                        op['without_nds_sum']=float(op['price_sum']) - float(op['nds_sum'])
                        op['logistik_cheb_sum']=op['quantity_sum'] * int(log_cheb)
                        op['all_item_sers_sum']=float(summ) * float(op['quantity_sum'])
                        op['kom_sb_sum']=float(comission) * op['quantity_sum']
                        op['obj_sum_rash_mp_sum']=op['all_item_sers_sum'] + op['kom_sb_sum'] + op['ekvaring']
                        op['sum_nds_sum']=op['obj_sum_rash_mp_sum'] *20/120
                        op['obj_sum_rash_mp_bez_sum']=op['obj_sum_rash_mp_sum']-op['sum_nds_sum']
                        op['sebestoimost_sum']=0
                        op['marj_dohod']=op['without_nds_sum']-op['logistik_cheb_sum']-op['obj_sum_rash_mp_bez_sum']-op['sebestoimost_sum']
                        op['nalog_pribil']=op['marj_dohod']*20/100
                        op['chist_pribil']=op['marj_dohod']-op['nalog_pribil']
                        op['rentabelnost']=op['chist_pribil'] / op['price_sum'] *100

                

            ozon_prod_list = [{k: "{:.2f}".format(v) if isinstance(v, float) else v for k, v in d.items()} for d in ozon_prod_list]




            product_ids_and_quantities_delivering = ozon_orders_delivering.values(
                    product_id=F('financialll_data__financialll_data_product__product_id')
                ).annotate(
                    quantity_sum=Sum('financialll_data__financialll_data_product__quantity'),
                    payout_sum=Round(Sum('financialll_data__financialll_data_product__payout'), output_field=FloatField()),
                    commission_amount_sum=Round(Sum('financialll_data__financialll_data_product__commission_amount'), output_field=FloatField()),
                    marketplace_service_item_deliv_to_customer_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_deliv_to_customer'), output_field=FloatField()),
                    marketplace_service_item_direct_flow_trans_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_direct_flow_trans'), output_field=FloatField()),
                    marketplace_service_item_dropoff_ff_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_dropoff_ff'), output_field=FloatField()),
                    marketplace_service_item_dropoff_pvz_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_dropoff_pvz'), output_field=FloatField()),
                    marketplace_service_item_dropoff_sc_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_dropoff_sc'), output_field=FloatField()),
                    marketplace_service_item_fulfillment_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_fulfillment'), output_field=FloatField()),
                    marketplace_service_item_pickup_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_pickup'), output_field=FloatField()),
                    marketplace_service_item_return_after_deliv_to_customer_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_return_after_deliv_to_customer'), output_field=FloatField()),
                    marketplace_service_item_return_flow_trans_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_return_flow_trans'), output_field=FloatField()),
                    marketplace_service_item_return_not_deliv_to_customer_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_return_not_deliv_to_customer'), output_field=FloatField()),
                    marketplace_service_item_return_part_goods_customer_sum=Round(Sum('financialll_data__financialll_data_product__ozonitemservices__marketplace_service_item_return_part_goods_customer'), output_field=FloatField()),
                ).order_by('product_id')


            for product in ozon_prod_list:
                product['sp_dost'] = get_new_value(product)

            # Сортировка списка по новому значению
            ozon_prod_list = sorted(ozon_prod_list, key=lambda x: x['sp_dost'])


            for product in ozon_prod_list:
                row = [
                    str(current_date.strftime('%d.%m.%Y')),
                    str(product['sp_dost']),
                    str(product['sku']),
                    str(product['name']),
                    str(product['quantity_sum']),
                    str(product['price_sum']),
                    str(product['nds_sum']),
                    str(product['without_nds_sum']),
                    str(product['ekvaring']),
                    str(product['logistik_cheb_sum']),
                    str(product['all_item_sers_sum']),
                    str(product['kom_sb_sum']),
                    str(product['obj_sum_rash_mp_sum']),
                    str(product['sum_nds_sum']),
                    str(product['obj_sum_rash_mp_bez_sum']),
                    str(product['sebestoimost_sum']),
                    str(product['marj_dohod']),
                    str(product['nalog_pribil']),
                    str(product['chist_pribil']),
                    str(product['rentabelnost']),
                ] 
                data.append(row)
            

            current_date += timedelta(days=1)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="marja_ozon.csv"'
        response['Content-Encoding'] = 'utf-8'
        response['Content-Type'] = 'text/csv; charset=utf-8'

        writer = csv.writer(response, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)

        for row in data:
            writer.writerow(row)

        return response


class api_upakovka_spisok_generate_csv(View):
    def get(self, request):


        market_place_type = request.GET.get('market_place_type', None)
        start_date = datetime.datetime.strptime(request.GET.get('report_date'), '%Y-%m-%d')

        start_of_day = datetime.datetime.combine(start_date, datetime.time.min)
        end_of_day = datetime.datetime.combine(start_date, datetime.time.max)

        # Заголовки для нашего CSV-файла
        fieldnames = [
            'type',
            'number',
            'fio',
            'artikul',
            'charackter',
            'kolvo',
            'cena',
            'data'
            ]
        
        data = []
        data.append(fieldnames) 

        if market_place_type == "Ozon" or market_place_type == 'all':
        
            order_list = OzonPosting.objects.filter(delivering_date__range=(start_of_day, end_of_day)).exclude(status="cancelled", delivery_method=None)

            for order in order_list:
                finans = Ozon_FinancialData.objects.filter(ozon_posting=order)
                for fin in finans:
                    prod_list = Ozon_Products.objects.filter(financial_data=fin)
                    for prod in prod_list:

                        get = Ozon_ProductList.objects.get(product_id=prod.product_id)
                        kk = ''
                        try:
                            product = MpProduct.objects.get(artikul=get.offer_id)
                            chars = product.characteristics.all()
                            
                            for characteristic in chars:
                                product_characteristic = ProductCharacteristic.objects.get(product=product, characteristic=characteristic)
                                kk = kk + characteristic.name + ': ' + product_characteristic.value +', '
                            product_name = product.artikul

                        except ObjectDoesNotExist:
                            art =  'Артикул' +get.offer_id+ 'не найден в базе артиклов'
                            product_name = get.offer_id


                        if order.customer:
                            customer_name = order.customer.name
                            
                        else:
                            customer_name = 'Пользователь скрыт'
                            pass
                        row = [
                            'ozon',
                            str(order.posting_number),
                            str(customer_name),
                            str(product_name),
                            str(kk),
                            str(prod.quantity),
                            str(prod.price),
                            str(order.delivering_date),
                        ]
                        data.append(row)

        if market_place_type == "Ya" or market_place_type == 'all':

            if start_date:
                filters = {'shipment_posting_date__range': (start_of_day, end_of_day)}

            # Load all order_list with related items
            order_list = YaOrder.objects.filter(**filters).exclude(status='CANCELLED')

            for order in order_list:
                for prod in order.items.all():
                    kk = ''
                    try:
                        product = MpProduct.objects.get(artikul=prod.offer_id)
                        chars = product.characteristics.all()
                        
                        for characteristic in chars:
                            product_characteristic = ProductCharacteristic.objects.get(product=product, characteristic=characteristic)
                            kk = kk + characteristic.name + ': ' + product_characteristic.value +', '
                            product_name = product.artikul

                    except ObjectDoesNotExist:
                            kk =  'Артикул' +prod.offer_id+ 'не найден в базе артиклов'
                            product_name = prod.offer_id

                    row = [
                            'ya.market',
                            str(order.id_order),
                            str('покупатель скрыт'),
                            str(product_name),
                            str(kk),
                            str(prod.count),
                            str(prod.buyer_price),
                            str(start_date),
                        ]
                    data.append(row)

        if market_place_type == "smm" or market_place_type == 'all':

            if start_date:
                filters = { 'shipment_posting_date__range': (start_of_day, end_of_day)}

            order_list = SMMShipment.objects.filter(**filters).exclude(status='CUSTOMER_CANCELED')


            for order in order_list:
                for prod in order.items.all():
                    kk = ''
                    try:
                        product = MpProduct.objects.get(artikul=prod.offerId)
                        chars = product.characteristics.all()
                        
                        for characteristic in chars:
                            product_characteristic = ProductCharacteristic.objects.get(product=product, characteristic=characteristic)
                            kk = kk + characteristic.name + ': ' + product_characteristic.value +', '
                            product_name = product.artikul
                    except ObjectDoesNotExist:
                            kk =  'Артикул' +prod.offerId+ 'не найден в базе артиклов'
                            product_name = prod.offerId

                    row = [
                            'smm',
                            str(order.shipmentId),
                            str(order.customerFullName),
                            str(product_name),
                            str(kk),
                            str(prod.quantity),
                            str(prod.price),
                            str(order.shipment_posting_date),
                        ]
                    data.append(row)




        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="marja_ozon.csv"'
        response['Content-Encoding'] = 'utf-8'
        response['Content-Type'] = 'text/csv; charset=utf-8'

        writer = csv.writer(response, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)

        for row in data:
            writer.writerow(row)

        return response




class SberMegaMarket:
    def __init__(self):
        self.url = "https://api.megamarket.tech/api/"
        self.smm_settings = SMM_Settings.objects.all()  # извлекаем все объекты
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def MakerResponse(self, method, body=None):
        body = json.dumps(body) if body else body
        response = requests.get(self.url + method, headers=self.headers, data=body)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def GetAllOrders(self):

        method = "market/v1/orderService/order/search"
        now = datetime.datetime.utcnow()
        dt_from = (now - datetime.timedelta(days=30)).isoformat()+"Z"

        # обрабатываем каждый объект настроек
        for smm_setting in self.smm_settings:
            shop_id_api = smm_setting.shop_id
            body = {
                    "data": {
                        "token": smm_setting.token,
                        "dateFrom": dt_from,
                        "dateTo": now.isoformat()+"Z",
                        "count": 1000,
                        "statuses": [
                            "NEW",
                            "CONFIRMED",
                            "PACKED",
                            "PACKING_EXPIRED",
                            "SHIPPED",
                            "DELIVERED",
                            "MERCHANT_CANCELED",
                            "CUSTOMER_CANCELED"
                        ]
                    },
                    "meta": {}
                }

            response = self.MakerResponse(method, body)
            if response and 'data' in response and isinstance(response['data'], dict):
                shipment_ids = []  
                print(len(response['data']['shipments']))
                for order in response['data']['shipments']:
                    order_data = json.loads(order)
                    shipment_ids.append(order_data) 
                self.GetShipmentInfo(smm_setting.token, shipment_ids, shop_id_api)  
            else:
                print("Response contains no data or it's not valid")


    def GetShipmentInfo(self, token, shipment_ids, shop_id_api):
        method = "market/v1/orderService/order/get"

        shipment_id_groups = list(chunks(shipment_ids, 10))

        for group in shipment_id_groups:
            body = {
                "meta": {},
                "data": {
                    "token": token,
                    "shipments": group  # передаем список идентификаторов отправлений
                }
            }
            response = self.MakerResponse(method, body)
            if response and 'data' in response:
                self.get_shipment_info(response, shop_id_api)
            else:
                print("Response contains no data")

    def get_shipment_info(self, response, shop_id_api):
        data = response
        
        if not data.get('data') or not data['data'].get('shipments'):
            print('No shipments in response')
            return

        for shipment_data in data['data']['shipments']:
            if shipment_data.get('shippingPoint') == '':
                shippingPoint = 96775
                
            else:
                shippingPoint = shipment_data.get('shippingPoint')
            shipment, created = SMMShipment.objects.update_or_create(
                    shipmentId=shipment_data.get('shipmentId'),
                    defaults={
                        'orderCode': shipment_data.get('orderCode'),
                        'confirmedTimeLimit': shipment_data.get('confirmedTimeLimit'),
                        'packingTimeLimit':  shipment_data.get('packingTimeLimit'),
                        'shippingTimeLimit':  shipment_data.get('shippingTimeLimit'),
                        'shipmentDateFrom': shipment_data.get('shipmentDateFrom'),
                        'shipmentDateTo': shipment_data.get('shipmentDateTo'),
                        'deliveryId':  shipment_data.get('deliveryId'),
                        'shipmentDateShift': shipment_data.get('shipmentDateShift'),
                        'shipmentIsChangeable': shipment_data.get('shipmentIsChangeable'),
                        'customerFullName': shipment_data.get('customerFullName'),
                        'customerAddress': shipment_data.get('customerAddress'),
                        'shippingPoint': shippingPoint,
                        'creationDate': shipment_data.get('creationDate'),
                        'deliveryDate': parse_datetime(shipment_data.get('deliveryDate')),
                        'deliveryDateFrom': shipment_data.get('deliveryDateFrom'),
                        'deliveryDateTo': shipment_data.get('deliveryDateTo'),
                        'deliveryMethodId': shipment_data.get('deliveryMethodId'),
                        'depositedAmount': shipment_data.get('depositedAmount'),
                        'status': shipment_data.get('status'),
                        'id_shop_api': shop_id_api,
                        'packingDate': shipment_data.get('packingDate')
                    }
                )
            shipment.save()

            for item_data in shipment_data.get('items', []):
                goods_data, created = SMMGoodsData.objects.update_or_create(
                    name=item_data['goodsData'].get('name'),
                    category_name=item_data['goodsData'].get('categoryName', ""),
                )
                goods_data.save()

                delivery_date = parse_datetime(shipment_data.get('deliveryDate'))


                item, created = SMMItem.objects.update_or_create(
                    shipment=shipment,
                    itemIndex=item_data.get('itemIndex'),
                    defaults={
                        'itemIndex': item_data.get('itemIndex'),
                        'status': item_data.get('status'),
                        'goodsData': goods_data,
                        'subStatus': item_data.get('subStatus'),
                        'price': item_data.get('price'),
                        'finalPrice': item_data.get('finalPrice'),
                        'quantity': item_data.get('quantity'),
                        'offerId': item_data.get('offerId'),
                        'goodsId': item_data.get('goodsId'),
                        'boxIndex': item_data.get('boxIndex'),
                    }
                )
                item.save()

                # Save all discounts for the current item
                for discount_data in item_data['discounts']:
                    SMMDiscount.objects.update_or_create(
                        item=item,
                        discountType=discount_data['discountType'],
                        defaults={
                            'discountDescription': discount_data['discountDescription'],
                            'discountAmount': discount_data['discountAmount'],
                        }
                    )

                for events in item_data['events']:
                    event, created = SMMEvent.objects.update_or_create(
                        smm_item=item,
                        eventDate=events['eventDate'],
                        defaults={
                            'eventName': events['eventName'],
                            'eventValue': events['eventValue'],
                        }
                    )
                    event.save()

class Ozon:
    def __init__(self):
        self.url = "https://api-seller.ozon.ru"
        ozon_settings_bd = Ozon_Settings.objects.get(id=1)
        self.head = {
                "Client-Id": ozon_settings_bd.client_id,
                "Api-Key": ozon_settings_bd.client_key           
        }

    def MakerResponse(self, method, body):
        print(f"Делаем запрос OZON meth: {method} \n telo: {body}")
        body = json.dumps(body)
        response = requests.post(self.url + method, headers=self.head, data=body)
        if response.status_code == 200:
            print(f"Запрос Верен")
            return response.json()
        else:
            print(f"Ошибка запроса {response.content}")
            return None

    def GetProductInJoMarja(self, client_id, sku_list):
        clent = Ozon_Settings.objects.get(client_id=client_id)
        method = "/v2/product/info"
        response = {'result': []}
        self.head = {
                    "Client-Id": clent.client_id,
                    "Api-Key": clent.client_key           
            }
        sku_list = sku_list.values_list('sku', flat=True)
        sku_list = [{'sku': name} for name in sku_list]
        for sku in sku_list:
            method = "/v2/product/info"
            body = {
                'sku': int(sku['sku']),
            }
            result = self.MakerResponse(method, body)
            if result:
                response['result'].append(result['result'])
            else:
                method = "/v1/product/info/discounted"
                body = {
                    'discounted_skus': [int(sku['sku'])],
                }
                result = self.MakerResponse(method, body)
                if result:
                    print(result)
                    for item in result['items']:
                        response['result'].append(item)
                        method = "/v2/product/info"
                        body = {
                            'sku': int(item['sku']),
                        }
                        result = self.MakerResponse(method, body)
                        if result:
                            result['result']['sku'] = int(sku['sku'])
                            response['result'].append(result['result'])
        return response

    def GetProductInToMile(self, client_id, sku):
        clent = Ozon_Settings.objects.get(client_id=client_id)
        method = "/v4/product/info/prices"
        self.head = {
                    "Client-Id": clent.client_id,
                    "Api-Key": clent.client_key           
            }
        body = {
                    "filter": {
                        "offer_id": sku,
                        "visibility": "ALL"
                    },
                    "last_id": "",
                    "limit": 1000
                }

        response = self.MakerResponse(method, body)
        return response

    def get_orders(self):
        print(self.client_id)

    def GetOrders(self, date_to, date_from):
        OzonClients = Ozon_Settings.objects.all()
        for OzonClient in OzonClients:
            self.head = {
                    "Client-Id": OzonClient.client_id,
                    "Api-Key": OzonClient.client_key           
            }

            method = "/v2/posting/fbo/list"
            body = {
                    "dir": "desc",
                    "filter": {
                        "since": date_from+"T00:00:00.000Z",
                        "to": date_to+"T23:59:59.000Z"
                    },
                    "limit": 1000,
                    "offset": 0,
                    "translit": True,
                    "with": {
                        "analytics_data": True,
                        "financial_data": True
                    }
                    }

            response = self.MakerResponse(method, body)
            if 'result' in response:
                # Create a new dictionary with 'postings' key
                new_data = {'postings': response['result']}
                # Replace 'result' key with 'postings' key
                data = new_data
            data = {'result': new_data}
            self.fbo_insert_update_postings(data = data, client_id=OzonClient.client_id)
        for OzonClient in OzonClients:
            i=0
            while i<5:
                self.head = {
                        "Client-Id": OzonClient.client_id,
                        "Api-Key": OzonClient.client_key           
                }

                method = "/v3/posting/fbs/list"
                body = {
                        "dir": "desc",
                        "filter": {
                            "since": date_from+"T00:00:00.000Z",
                            "to": date_to+"T23:59:59.000Z"
                        },
                        "limit": 1000,
                        "offset": i*1000,
                        "translit": True,
                        "with": {
                            "analytics_data": True,
                            "financial_data": True
                        }
                        }

                response = self.MakerResponse(method, body)
                self.insert_update_postings(data = response, client_id=OzonClient.client_id)
                i += 1

        return response
    
    def GetProdInfo(self, offer_id, sku=None, client_id=None):
        if sku:
            OzonClients = Ozon_Settings.objects.get(client_id=client_id)
            self.head = {
                    "Client-Id": OzonClients.client_id,
                    "Api-Key": OzonClients.client_key           
            }
            method = "/v2/product/info"
            body = {
                "sku": int(sku)
                }

            response = self.MakerResponse(method, body)

            return response
        else:
            method = "/v2/product/info"
            body = {
                "offer_id": offer_id
                }

            response = self.MakerResponse(method, body)

        return response
    
    def GetListTransaсtion(self, date_from, date_to):
        OzonClients = Ozon_Settings.objects.all()
        response_list = []
        for OzonClient in OzonClients:
            self.head = {
                    "Client-Id": OzonClient.client_id,
                    "Api-Key": OzonClient.client_key           
            }
            method = "/v3/finance/transaction/list"
            body = {
            "filter": {
                "date": {
                "from": f"{date_from}T00:00:00.000Z",
                "to": f"{date_to}T23:59:59.000Z"
                },
                "operation_type": [],
                "posting_number": "",
                "transaction_type": "all"
            },
            "page": 1,
            "page_size": 1000
            }
            response = self.MakerResponse(method, body)
            if response is None:
                print("")
                
            else:
               response_list.append(response)  # добавьте ответ в список
           
        return response_list
    
    def TotalTranz(self, date_from, date_to):
        method = "/v3/finance/transaction/totals"
        body = {
            "date": {
            "from": date_from+"T00:00:00.000Z",
            "to": date_to+"T23:59:59.000Z"
            },
            "posting_number": "",
            "transaction_type": "all"
            }

        response = self.MakerResponse(method, body)

        return response
    

    def Prod_list_get(self):
        OzonClients = Ozon_Settings.objects.all()
        for OzonClient in OzonClients:
            self.head = {
                    "Client-Id": OzonClient.client_id,
                    "Api-Key": OzonClient.client_key           
            }
            method = "/v2/product/list"
            body = {
                "filter": {
                "visibility": "ALL"
                },
                "last_id": "",
                "limit": 1000
                }
            response = self.MakerResponse(method, body)
            if response is None:
                print("")
                
            else:
                for result in response['result']['items']:
                    posting_services = result

                    defaults = {}
                    for key in posting_services.keys():
                            defaults[key] = posting_services[key]
                            obj, _  = Ozon_ProductList.objects.update_or_create(
                            product_id=result['product_id'],
                            defaults=defaults, 
                            client_id=OzonClient.client_id 
                            )

            
           
        return True


    def Prod_list_getIS(self, offer_id):
        OzonClients = Ozon_Settings.objects.all()
        for OzonClient in OzonClients:
            self.head = {
                    "Client-Id": OzonClient.client_id,
                    "Api-Key": OzonClient.client_key           
            }
            method = "/v2/product/info"
            body = {
                "sku": offer_id
            }
            response = self.MakerResponse(method, body)
            if response is None:
                print("")
                
            else:
                obj, created = Ozon_ProductList.objects.update_or_create(
                    product_id=offer_id,
                    defaults={
                        'offer_id': response['result']['offer_id'], 
                        'client_id': OzonClient.client_id 
                    }
                )

        return True


    def SpisSklad(self):
        OzonClients = Ozon_Settings.objects.all()
        for OzonClient in OzonClients:
            self.head = {
                    "Client-Id": OzonClient.client_id,
                    "Api-Key": OzonClient.client_key           
            }
            method = "/v1/warehouse/list"
            body = { }

            response = self.MakerResponse(method, body)
            for result in response['result']:
                posting_services = result

                defaults = {}
                for key in posting_services.keys():
                        defaults[key] = posting_services[key]
                warehause, _ = Ozon_Warehouse.objects.update_or_create(
                    warehouse_id=result['warehouse_id'],
                    defaults=defaults, 
                    client_id=OzonClient.client_id 
                )

        return

    def fbo_insert_update_postings(self, data, client_id):
            for posting_data in data['result']['postings']:

                # Создание или обновление модели DeliveryMethod
                if 'delivery_method' in posting_data:
                    delivery_method, _ = OzonDeliveryMethod.objects.update_or_create(
                        id=posting_data['delivery_method']['id'], 
                        defaults=posting_data['delivery_method'])
                else:
                    delivery_method=None

                if 'cancellation' in posting_data:
                    # Создание или обновление модели Cancellation
                    cancellation, _ = OzonCancellation.objects.update_or_create(
                        cancel_reason_id=posting_data['cancellation']['cancel_reason_id'], 
                        defaults=posting_data['cancellation'])
                else:
                    cancellation=None


                if 'customer' in posting_data and posting_data['customer']['address']['address_tail'] != None:
                    address, _ = OzonAddress.objects.update_or_create(
                            address_tail=posting_data['customer']['address']['address_tail'], 
                            defaults=posting_data['customer']['address'])
                else:
                    customer = None
                
                # Создание или обновление модели Customer

                if 'customer' in posting_data:
                    customer, _ = OzonCustomer.objects.update_or_create(
                        customer_id=posting_data['customer']['customer_id'], 
                        defaults={
                            **posting_data['customer'],
                            'address': address # Здесь добавляем ссылку на модель адреса
                        })
                else:
                    customer = None
                

                client_id = int(client_id)
                # Создание или обновление модели Posting
                posting_data = {k: v for k, v in posting_data.items() if k != 'products'}
                posting, _ = OzonPosting.objects.update_or_create(
                    posting_number=posting_data['posting_number'],
                    defaults={
                        **posting_data,
                        'delivery_method': delivery_method,
                        'cancellation': cancellation,
                        'customer': customer,
                        'mandatory_mark': '',
                        'addressee': '',
                        'barcodes': '',
                        'analytics_data': '',
                        'financial_data': '',
                        'available_actions': '',
                        'requirements': '',
                        'client_id': client_id
                    })
                posting.save()

                # Создание или обновление моделей Product
                product_ids = []
                if 'products' in posting_data:
                    for product_data in posting_data['products']:
                        product, _ = OzonProduct.objects.update_or_create(
                            ozon_posting=posting, 
                            defaults={**product_data, 'sebestoimist':0})
                        product_ids.append(product.id)
                    posting.products.set(product_ids)


                if posting_data['analytics_data']:
                    posting_services = posting_data['analytics_data']

                    defaults = {}
                    for key in posting_services.keys():
                        defaults[key] = posting_services[key]

                    Analytics_data, _ = Ozon_Analytics_data.objects.update_or_create(
                        ozon_posting=posting,
                        defaults=defaults
                    )

                if posting_data['financial_data']:
                    FinancialData, _ = Ozon_FinancialData.objects.update_or_create(
                        ozon_posting=posting,
                        defaults={
                            'cluster_from': posting_data['financial_data']['cluster_from'],
                            'cluster_to': posting_data['financial_data']['cluster_to'],
                        }
                    )

                    posting_services = posting_data['financial_data']['posting_services']

                    if posting_services != None:
                        defaults = {}
                        for key in posting_services.keys():
                            defaults[key] = posting_services[key]

                        PostingServices, _ = Ozon_PostingServices.objects.update_or_create(
                            financial_data=FinancialData,
                            defaults=defaults
                        )

                    for product_data in posting_data['financial_data']['products']:
                        product, _ = Ozon_Products.objects.update_or_create(
                            financial_data=FinancialData, 
                            defaults={
                                    "actions" : product_data['actions'],
                                    "currency_code" : product_data['currency_code'],
                                    "client_price" : product_data['client_price'],
                                    "commission_amount" : product_data['commission_amount'],
                                    "commission_percent": product_data['commission_percent'],
                                    "old_price" : product_data['old_price'],
                                    "payout" : product_data['payout'],
                                    "price" : product_data['price'],
                                    "product_id" : product_data['product_id'],
                                    "quantity" : product_data['quantity'],
                                    "total_discount_percent" : product_data['total_discount_percent'],
                                    "total_discount_value" : product_data['total_discount_value'],
                                
                                })

                        PostingServices,_ = Ozon_ItemServices.objects.update_or_create(
                            product=product,
                            defaults= {
                            "marketplace_service_item_deliv_to_customer" : product_data['item_services']['marketplace_service_item_deliv_to_customer'],
                            'marketplace_service_item_direct_flow_trans' : product_data['item_services']['marketplace_service_item_direct_flow_trans'],
                            'marketplace_service_item_dropoff_ff' : product_data['item_services']['marketplace_service_item_dropoff_ff'],
                            'marketplace_service_item_dropoff_pvz' : product_data['item_services']['marketplace_service_item_dropoff_pvz'],
                            'marketplace_service_item_dropoff_sc' : product_data['item_services']['marketplace_service_item_dropoff_sc'],
                            'marketplace_service_item_fulfillment' : product_data['item_services']['marketplace_service_item_fulfillment'],
                            'marketplace_service_item_pickup' : product_data['item_services']['marketplace_service_item_pickup'],
                            'marketplace_service_item_return_after_deliv_to_customer' : product_data['item_services']['marketplace_service_item_return_after_deliv_to_customer'],
                            'marketplace_service_item_return_flow_trans' : product_data['item_services']['marketplace_service_item_return_flow_trans'],
                            'marketplace_service_item_return_not_deliv_to_customer' : product_data['item_services']['marketplace_service_item_return_not_deliv_to_customer'],
                            'marketplace_service_item_return_part_goods_customer' : product_data['item_services']['marketplace_service_item_return_part_goods_customer'],
                            }
                        )


                

            print(f"Были внесены и изменены заказы OZON")
            return 



    def insert_update_postings(self, data, client_id):
            for posting_data in data['result']['postings']:
                # Создание или обновление модели DeliveryMethod
    
                try:
                    warehause = Ozon_Warehouse.objects.get(warehouse_id=posting_data['delivery_method']['warehouse_id'])
                except Ozon_Warehouse.DoesNotExist:
                    warehause = self.SpisSklad()
                    warehause = Ozon_Warehouse.objects.get(warehouse_id=posting_data['delivery_method']['warehouse_id'])
                delivery_method, created = OzonDeliveryMethod.objects.update_or_create(
                    id=posting_data['delivery_method']['id'], 
                    defaults={
                        **posting_data['delivery_method'],
                        'warehouse_id': warehause
                    })
                                
             
                # Создание или обновление модели Cancellation
                cancellation, _ = OzonCancellation.objects.update_or_create(
                    cancel_reason_id=posting_data['cancellation']['cancel_reason_id'], 
                    defaults=posting_data['cancellation'])


                # Создание или обновление модели Address
                if posting_data['customer'] is None:
                    customer = None
                else:
                    address, _ = OzonAddress.objects.update_or_create(
                        address_tail=posting_data['customer']['address']['address_tail'], 
                        defaults=posting_data['customer']['address'])
                
                # Создание или обновление модели Customer

                if posting_data['customer'] is None:
                    customer = None
                else:
                    customer, _ = OzonCustomer.objects.update_or_create(
                        customer_id=posting_data['customer']['customer_id'], 
                        defaults={
                            **posting_data['customer'],
                            'address': address # Здесь добавляем ссылку на модель адреса
                        })
                
                # Создание или обновление моделей Product
                product_ids = []
                for product_data in posting_data['products']:
                    product, _ = OzonProduct.objects.update_or_create(
                        sku=product_data['sku'], 
                        defaults={**product_data, 'sebestoimist':0})
                    product_ids.append(product.id)
                client_id = int(client_id)
                # Создание или обновление модели Posting
                posting_data = {k: v for k, v in posting_data.items() if k != 'products'}
                posting, _ = OzonPosting.objects.update_or_create(
                    posting_number=posting_data['posting_number'],
                    defaults={
                        **posting_data,
                        'delivery_method': delivery_method,
                        'cancellation': cancellation,
                        'customer': customer,
                        'mandatory_mark': '',
                        'addressee': '',
                        'barcodes': '',
                        'analytics_data': '',
                        'financial_data': '',
                        'available_actions': '',
                        'requirements': '',
                        'client_id': client_id
                    })
                posting.save()


                if posting_data['analytics_data']:
                    posting_services = posting_data['analytics_data']

                    defaults = {}
                    for key in posting_services.keys():
                        defaults[key] = posting_services[key]

                    Analytics_data, _ = Ozon_Analytics_data.objects.update_or_create(
                        ozon_posting=posting,
                        defaults=defaults
                    )

                if posting_data['financial_data']:
                    FinancialData, _ = Ozon_FinancialData.objects.update_or_create(
                        ozon_posting=posting,
                        defaults={
                            'cluster_from': posting_data['financial_data']['cluster_from'],
                            'cluster_to': posting_data['financial_data']['cluster_to'],
                        }
                    )

                    posting_services = posting_data['financial_data']['posting_services']

                    defaults = {}
                    for key in posting_services.keys():
                        defaults[key] = posting_services[key]

                    PostingServices, _ = Ozon_PostingServices.objects.update_or_create(
                        financial_data=FinancialData,
                        defaults=defaults
                    )

                    for product_data in posting_data['financial_data']['products']:
                        product, _ = Ozon_Products.objects.update_or_create(
                            financial_data=FinancialData, 
                            defaults={
                                    "actions" : product_data['actions'],
                                    "currency_code" : product_data['currency_code'],
                                    "client_price" : product_data['client_price'],
                                    "commission_amount" : product_data['commission_amount'],
                                    "commission_percent": product_data['commission_percent'],
                                    "old_price" : product_data['old_price'],
                                    "payout" : product_data['payout'],
                                    "price" : product_data['price'],
                                    "product_id" : product_data['product_id'],
                                    "quantity" : product_data['quantity'],
                                    "total_discount_percent" : product_data['total_discount_percent'],
                                    "total_discount_value" : product_data['total_discount_value'],
                                
                                })

                        PostingServices,_ = Ozon_ItemServices.objects.update_or_create(
                            product=product,
                            defaults= {
                            "marketplace_service_item_deliv_to_customer" : product_data['item_services']['marketplace_service_item_deliv_to_customer'],
                            'marketplace_service_item_direct_flow_trans' : product_data['item_services']['marketplace_service_item_direct_flow_trans'],
                            'marketplace_service_item_dropoff_ff' : product_data['item_services']['marketplace_service_item_dropoff_ff'],
                            'marketplace_service_item_dropoff_pvz' : product_data['item_services']['marketplace_service_item_dropoff_pvz'],
                            'marketplace_service_item_dropoff_sc' : product_data['item_services']['marketplace_service_item_dropoff_sc'],
                            'marketplace_service_item_fulfillment' : product_data['item_services']['marketplace_service_item_fulfillment'],
                            'marketplace_service_item_pickup' : product_data['item_services']['marketplace_service_item_pickup'],
                            'marketplace_service_item_return_after_deliv_to_customer' : product_data['item_services']['marketplace_service_item_return_after_deliv_to_customer'],
                            'marketplace_service_item_return_flow_trans' : product_data['item_services']['marketplace_service_item_return_flow_trans'],
                            'marketplace_service_item_return_not_deliv_to_customer' : product_data['item_services']['marketplace_service_item_return_not_deliv_to_customer'],
                            'marketplace_service_item_return_part_goods_customer' : product_data['item_services']['marketplace_service_item_return_part_goods_customer'],
                            }
                        )


                posting.products.set(product_ids)

            print(f"Были внесены и изменены заказы OZON")
            return 


class YaMarket:
    def __init__(self):
        self.client_id = "9217e2b96fec4861b5145f85c921d87e"
        self.client_secret = "4c2b8234bce04a65957ca0d3e9ec3517"
        self.token = "y0_AgAAAAA8S82wAArHcgAAAADxPkHBbk5IGIT6RfuAXiib0FmyXasVh1I"
        self.header ={
            'Authorization': "Bearer " + self.token, "Client-ID": self.client_id, 'Content-Type': 'application/json'
        }

    def MakerResponse(self, method, body, type):
        if type=="get":
            print(f"Делаем запрос Я.Маркет Метод: {method} \nТело: {body}\n")
            response = requests.get(method, headers=self.header, params=body)
            if response.status_code == 200:
                print(f"Запрос Верен\n")
                return response.json()
            else:
                print(f"Ошибка запроса")
                return None
        else:
            print(f"Делаем запрос Я.Маркет Метод: {method} \nТело: {body}\n")
            body = json.dumps(body)
            response = requests.post(method, headers=self.header, json=body)
            if response.status_code == 200:
                print(f"Запрос Верен")
                return response.json()
            else:
                print(f"Ошибка запроса")
                print(response)
                return None
        
    def GetCompany(self):
        self.method = "https://api.partner.market.yandex.ru/campaigns"
        self.type="get"
        body = {
            'page': 1,
            'pageSize': 20
        }
        response = self.MakerResponse(method=self.method, body= body, type=self.type)
        return response

    def GetShopInfo(self, shop__id=None):
        self.method = f"https://api.partner.market.yandex.ru/campaigns/{shop__id}/"
        self.type="get"
        body = {

        }
        response = self.MakerResponse(method=self.method, body= body, type=self.type)
        return response
    
    def process_order(self, order, id_shop):
                order_list=order
                if order == None:
                    print("Ошибка получения данных")
                else:
                    t = 0
                    for order in order_list['orders']:
                        t=t+1
                        id_order=order.get('id')
                        shipmentDate = None
                        if 'shipmentDate' in order['delivery']['shipments'][0]:
                            shipmentDate = order['delivery']['shipments'][0]['shipmentDate']
                            shipmentDate = parse_date_or_datetime(shipmentDate)

                        ya_order, created = YaOrder.objects.update_or_create(
                            id_order=id_order,
                            defaults={
                                'status': order['status'],
                                'substatus': order['substatus'],
                                'creation_date': datetime.datetime.strptime(order['creationDate'], "%d-%m-%Y %H:%M:%S").isoformat(" "),
                                'items_total': order['itemsTotal'],
                                'total': order['total'],
                                'delivery_total': order['deliveryTotal'],
                                'subsidy_total': order['subsidyTotal'],
                                'total_with_subsidy': order['totalWithSubsidy'],
                                'buyer_items_total': order['buyerItemsTotal'],
                                'buyer_total': order['buyerTotal'],
                                'buyer_items_total_before_discount': order['buyerItemsTotalBeforeDiscount'],
                                'buyer_total_before_discount': order['buyerTotalBeforeDiscount'],
                                'payment_type': order['paymentType'],
                                'payment_method': order['paymentMethod'],
                                'fake': order['fake'],
                                # Update with a real shop id value when available
                                'id_shop': id_shop,
                                'shipmentDate': shipmentDate
                            }
                        )
                        ya_order.save()

                        for item in order['items']:
                            if 'feedId' in item:
                                YaItem.objects.update_or_create(
                                    ya_order=ya_order,
                                    id_item=item['id'],
                                    defaults={
                                        'feed_id': item['feedId'],
                                        'offer_id': item['offerId'],
                                        'feed_category_id': item['feedCategoryId'],
                                        'offer_name': item['offerName'],
                                        'price': item['price'],
                                        'buyer_price': item['buyerPrice'],
                                        'buyer_price_before_discount': item['buyerPriceBeforeDiscount'],
                                        'price_before_discount': item['priceBeforeDiscount'],
                                        'count': item['count'],
                                        'vat_status': item['vat'],
                                        'shop_sku': item['shopSku'],
                                        'subsidy': item['subsidy'],
                                        'partner_warehouse_id': item['partnerWarehouseId'],
                                    }
                                )
                            else:
                                YaItem.objects.update_or_create(
                                    ya_order=ya_order,
                                    id_item=item['id'],
                                    defaults={
                                        'offer_id': item['offerId'],
                                        'feed_category_id': item['feedCategoryId'],
                                        'offer_name': item['offerName'],
                                        'price': item['price'],
                                        'buyer_price': item['buyerPrice'],
                                        'buyer_price_before_discount': item['buyerPriceBeforeDiscount'],
                                        'price_before_discount': item['priceBeforeDiscount'],
                                        'count': item['count'],
                                        'vat_status': item['vat'],
                                        'shop_sku': item['shopSku'],
                                        'subsidy': item['subsidy'],
                                        'partner_warehouse_id': item['partnerWarehouseId'],
                                    }
                                )

                        delivery = order['delivery']
                        addresse = order.get('delivery', None)
                        addresse = addresse.get('address', None)
                        adress = ""
                        if addresse:
                            country = addresse.get('country', None)
                            city= addresse.get('city', None)
                            district= addresse.get('district', None)
                            house= addresse.get('house', None)
                            entrance= addresse.get('entrance', None)
                            entryphone= addresse.get('entryphone', None)
                            floor= addresse.get('floor', None)
                            apartment= addresse.get('apartment', None)

                            if country:
                                adress = adress + country+", "

                            if city:
                                adress = adress + city+", "

                            if district:
                                adress = adress + district+", "

                            if house:
                                adress = adress + house+", "

                            if entrance:
                                adress = adress + entrance+", "

                            if entryphone:
                                adress = adress + entryphone+", "

                            if floor:
                                adress = adress + floor+", "

                            if apartment:
                                adress = adress + apartment+", "

                        YaDelivery.objects.update_or_create(
                            ya_order=ya_order,
                            defaults={
                                'type': delivery['type'],
                                'service_name': delivery['serviceName'],
                                'price': delivery['price'],
                                'delivery_partner_type': delivery['deliveryPartnerType'],
                                'from_date': datetime.datetime.strptime(delivery['dates']['fromDate'], "%d-%m-%Y").date(),
                                'to_date': datetime.datetime.strptime(delivery['dates']['toDate'], "%d-%m-%Y").date(),
                                'from_time': datetime.datetime.strptime(delivery['dates']['fromTime'], "%H:%M:%S").time(),
                                'to_time': datetime.datetime.strptime(delivery['dates']['toTime'], "%H:%M:%S").time(),
                                'region_name': delivery['region']['name'],
                                'region_type': delivery['region']['type'],
                                'city_name': delivery['region']['parent']['name'] if 'parent' in delivery['region'] and delivery['region']['type'].lower() == 'city_district' else None,
                                'city_type': adress,
                            }
                        )

                        if 'buyer' in order:
                            last_name = None
                            firstName = None
                            middleName = None
                            phone = None
                            email = None
                            type1 = None
                            
                            buyer = order['buyer']
                            if 'last_name' in buyer:
                                last_name = buyer['lastName']
                            if 'firstName' in buyer:
                                firstName = buyer['firstName']
                            if 'middleName' in buyer:
                                middleName = buyer['middleName']
                            if 'phone' in buyer:
                                phone = buyer['phone']
                            if 'email' in buyer:
                                email = buyer['email']
                            if 'type' in buyer:
                                last_name = buyer['type']
                            YaBuyer.objects.update_or_create(
                                ya_order=ya_order,
                                defaults={
                                    'last_name': last_name,
                                    'first_name': firstName,
                                    'middle_name': middleName,
                                    'phone': phone,
                                    'email': email,
                                    'type': type1
                                }
                            )
                    
    
    def GetOrders(self,campaignId):
        self.method = f"https://api.partner.market.yandex.ru/campaigns/{campaignId}/orders"
        self.type="get"
        body = {

        }
        response = self.MakerResponse(method=self.method, body= body, type=self.type)
        i=1

        if response and 'orders' in response:
            self.process_order(response, campaignId)

        if response and 'pagesCount' in response['pager'] and response['pager']['pagesCount']>1:
            while i < response['pager']['pagesCount']:
                i = i+1
                time.sleep(2)
                self.method = f'https://api.partner.market.yandex.ru/campaigns/{campaignId}/orders'
                self.type="get"
                body = {
                    'page': i,
                    'pageSize': 50
                }
                response_page = self.MakerResponse(method=self.method, body=body, type=self.type)    
                if response_page and 'pager' in response_page:
                    self.process_order(response_page, campaignId)
        return response
    


class PochtaRussia:
    def __init__(self):
        self.token = "jfLTstdteizM9ce1y5OZx5GdRuU15kDh"
        self.key_auth = "c3R1bGVybTRAZ21haWwuY29tOnN0dWxlcnBlZ2FzMjExcG9jaHRh"
        self.url = "https://otpravka-api.pochta.ru"

    def make_request(self, endpoint, method, data=None, params=None, headers=None):
        default_headers = {
            "Authorization": "AccessToken " + self.token,
            "X-User-Authorization":"Basic " + self.key_auth,
            'Content-Type': 'application/json',
            'Accept': 'application/json;charset=UTF-8',
        }
        if headers is not None:
            default_headers.update(headers)
        if method == 'GET':
            response = requests.get(self.url + endpoint, headers=default_headers, params=params)
        elif method == 'POST':
            response = requests.post(self.url + endpoint, headers=default_headers, data=data)
        else:
            raise ValueError("Invalid method. Only 'GET' and 'POST' are supported.")
        return response.json()

    def search_by_track_number(self, track_number):
        endpoint = "/1.0/shipment/search"
        params = {
            "query": str(track_number)
        }
        return self.make_request(endpoint, method='GET', params=params)

class PochtaRussiaNew:
    def __init__(self, my_login, my_password):
        self.url = 'https://tracking.russianpost.ru/rtm34?wsdl'
        self.my_login = my_login
        self.my_password = my_password

    def get_operation_history(self, barcode):
        self.barcode = barcode
        body = \
        """<?xml version="1.0" encoding="UTF-8"?>
                        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:oper="http://russianpost.org/operationhistory" xmlns:data="http://russianpost.org/operationhistory/data" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                        <soap:Header/>
                        <soap:Body>
                           <oper:getOperationHistory>
                              <data:OperationHistoryRequest>
                                 <data:Barcode>""" + self.barcode + """</data:Barcode>  
                                 <data:MessageType>0</data:MessageType>
                                 <data:Language>RUS</data:Language>
                              </data:OperationHistoryRequest>
                              <data:AuthorizationHeader soapenv:mustUnderstand="1">
                                 <data:login>"""+ self.my_login +"""</data:login>
                                 <data:password>""" + self.my_password + """</data:password>
                              </data:AuthorizationHeader>
                           </oper:getOperationHistory>
                        </soap:Body>
                     </soap:Envelope>"""

        self.make_request(body)

    def make_request(self, body):
        headers = {'Content-Type': 'text/xml'}
        response = requests.post(self.url, data=body, headers=headers)

        # Обработка ответа
        print(response.content)


class CDEK:
    def __init__(self):
        self.url = 'https://api.cdek.ru'
        self.Account = "WlPCUPYVmOphCUzix7RmTLkpi4CCAjqw"
        self.Secure_password = "HrmJOAMEH5DMt7fOnKxGJyF15rv06E79"
        self.access_token = self.get_access_token()

    def get_access_token(self):
        token_url = f"{self.url}/v2/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.Account,
            "client_secret": self.Secure_password
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    def make_request(self, endpoint, method, data=None, params=None, headers=None):
        default_headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Content-Type': 'application/json',
            'Accept': 'application/json;charset=UTF-8',
        }
        if headers is not None:
            default_headers.update(headers)

        url = f"{self.url}{endpoint}"
        if method == 'GET':
            response = requests.get(url, headers=default_headers, params=params)
        elif method == 'POST':
            if data is not None:
                data = json.dumps(data)  # Сериализация данных в JSON
            response = requests.post(url, headers=default_headers, data=data)
        else:
            raise ValueError("Invalid method. Only 'GET' and 'POST' are supported.")

        # Проверка статуса ответа и обработка ошибок
        if response.status_code >= 400:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

        return response.json()
    
    def get_order_info(self, order_number):
        endpoint = "/v2/orders/"
        data = {
            'cdek_number': order_number
        }

        return self.make_request(endpoint, method='GET', params=data)
    

class CDEK_Roznica:
    def __init__(self):
        self.url = 'https://api.cdek.ru'
        self.Account = "lvCDicFROesoS8cfPQ0KJg2wr185jDpJ"
        self.Secure_password = "GZGgVqZXHPwwnB4cmAFXcPrY8XAUdk0T"
        self.access_token = self.get_access_token()

    def get_access_token(self):
        token_url = f"{self.url}/v2/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.Account,
            "client_secret": self.Secure_password
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    def make_request(self, endpoint, method, data=None, params=None, headers=None):
        default_headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Content-Type': 'application/json',
            'Accept': 'application/json;charset=UTF-8',
        }
        if headers is not None:
            default_headers.update(headers)

        url = f"{self.url}{endpoint}"
        if method == 'GET':
            response = requests.get(url, headers=default_headers, params=params)
        elif method == 'POST':
            if data is not None:
                data = json.dumps(data)  # Сериализация данных в JSON
            response = requests.post(url, headers=default_headers, data=data)
        else:
            raise ValueError("Invalid method. Only 'GET' and 'POST' are supported.")

        # Проверка статуса ответа и обработка ошибок
        if response.status_code >= 400:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

        return response.json()
    
    def get_order_info(self, order_number):
        endpoint = "/v2/orders/"
        data = {
            'cdek_number': order_number
        }

        return self.make_request(endpoint, method='GET', params=data)