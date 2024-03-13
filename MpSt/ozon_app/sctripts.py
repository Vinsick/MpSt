import datetime
from .models import *
from .ozon_api import OzonAPI
from django.db import transaction

def UpdateWarehause(api_key):
    OzonClient = OzonAPI(api_key.client_id, api_key.client_key)
    response = OzonClient.GetWarehouseList()
    with transaction.atomic():
        for warehouse_data in response['result']:
            warehouse_id = warehouse_data.pop('warehouse_id')
            first_mile_type = warehouse_data.pop('first_mile_type')

            # Создаем или обновляем склад
            warehouse, created = OzonWarehouse.objects.update_or_create(
                warehouse_id=warehouse_id,
                defaults={
                    **warehouse_data,
                    'dropoff_point_id': first_mile_type['dropoff_point_id'],
                    'dropoff_timeslot_id': first_mile_type['dropoff_timeslot_id'],
                    'first_mile_is_changing': first_mile_type['first_mile_is_changing'],
                    'first_mile_type': first_mile_type['first_mile_type'],
                    'client_id': api_key,
                }
            )

            if created:
                pass
            else:
                warehouse.save()


def UpdateDeliveryMethod(api_key, warehouse_id):
    OzonClient = OzonAPI(api_key.client_id, api_key.client_key)
    response = OzonClient.GetDeliveryMethodList(warehouse_id)
    warehouse = OzonWarehouse.objects.get(warehouse_id=warehouse_id)
    for DM in response['result']:
        delivery_method, created = OzonDeliveryMethod.objects.update_or_create(
            id=DM['id'],
            defaults={
                **DM,
                'warehouse_id': warehouse,
                'client_id': api_key,
            }
        )

        if created:
            pass
        else:
            delivery_method.save()

def UpdateProductsList(api_key):
    OzonClient = OzonAPI(api_key.client_id, api_key.client_key)
    response = OzonClient.GetProductList()
    for product in response:
        product_, created = OzonProduct.objects.update_or_create(
            product_id=product['product_id'],
            defaults={
                **product,
                'client_id': api_key,
            }
        )
        if created:
            pass
        else:
            product_.save()

def Update_FBO_Posting_List(api_key):
    OzonClient = OzonAPI(api_key.client_id, api_key.client_key)
    date = datetime.datetime.today()
    from_date= date - datetime.timedelta(1)
    response = OzonClient.GetFBOPostingList(from_date.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))
    for Posting in response['result']:
        Posting_, created = OzonFBOPosting.objects.update_or_create(
            posting_number=Posting['posting_number'],
            defaults={
                'city': Posting['analytics_data']['city'],
                'delivery_type': Posting['analytics_data']['delivery_type'],
                'is_legal' : Posting['analytics_data']['is_legal'],
                'is_premium' : Posting['analytics_data']['is_premium'],
                'payment_type_group_name' : Posting['analytics_data']['payment_type_group_name'],
                'region' : Posting['analytics_data']['region'],
                'warehouse_id' : Posting['analytics_data']['warehouse_id'],
                'warehouse_name' : Posting['analytics_data']['warehouse_name'],
                'cancel_reason_id': Posting['cancel_reason_id'],
                'created_at' : Posting['created_at'],
                'in_process_at' : Posting['in_process_at'],
                'order_id' : Posting['order_id'],
                'order_number' : Posting['order_number'],
                'status' : Posting['status'],
                'client_id': api_key,
            }
        )

        if created:
            pass
        else:
            Posting_.save()

        for Product in Posting['products']:
            Product_, created = Ozon_FBO_Posting_Products.objects.update_or_create(
                fbo_postings=Posting_,
                offer_id = Product['offer_id'],
                defaults={
                    'digital_codes': Product['digital_codes'],
                    'name': Product['name'],
                    'offer_id' : Product['offer_id'],
                    'currency_code' : Product['currency_code'],
                    'price' : Product['price'],
                    'quantity' : Product['quantity'],
                    'sku' : Product['sku'],
                    'fbo_postings': Posting_,
                }
            )            
        if created:
            pass
        else:
            Product_.save()




        for FinancialProduct in Posting['financial_data']['products']:
            # Удаляем ключи 'actions' и 'picking' из FinancialProduct
            FinancialProduct.pop('actions', None)
            FinancialProduct.pop('picking', None)

            # Создаем отдельную переменную для item_services
            item_services = FinancialProduct.pop('item_services', None)

            # Теперь FinancialProduct не содержит этих ключей
            FinancialProduct_, created = OzonAllPostingFinancialProduct.objects.update_or_create(
                fbo_posting=Posting_,
                product_id=FinancialProduct['product_id'],
                defaults={
                    **FinancialProduct,
                    'marketplace_service_item_deliv_to_customer': item_services['marketplace_service_item_deliv_to_customer'],
                    'marketplace_service_item_direct_flow_trans': item_services['marketplace_service_item_direct_flow_trans'],
                    'marketplace_service_item_dropoff_ff': item_services['marketplace_service_item_dropoff_ff'],
                    'marketplace_service_item_dropoff_pvz': item_services['marketplace_service_item_dropoff_pvz'],
                    'marketplace_service_item_dropoff_sc': item_services['marketplace_service_item_dropoff_sc'],
                    'marketplace_service_item_fulfillment': item_services['marketplace_service_item_fulfillment'],
                    'marketplace_service_item_pickup': item_services['marketplace_service_item_pickup'],
                    'marketplace_service_item_return_after_deliv_to_customer': item_services['marketplace_service_item_return_after_deliv_to_customer'],
                    'marketplace_service_item_return_flow_trans': item_services['marketplace_service_item_return_flow_trans'],
                    'marketplace_service_item_return_not_deliv_to_customer': item_services['marketplace_service_item_return_not_deliv_to_customer'],
                    'marketplace_service_item_return_part_goods_customer': item_services['marketplace_service_item_return_part_goods_customer'],
                    'fbo_posting': Posting_,
                }
            )

            if created:
                pass
            else:
                FinancialProduct_.save()


def Update_FBS_Posting_List(api_key):
    OzonClient = OzonAPI(api_key.client_id, api_key.client_key)
    date = datetime.datetime.today()
    from_date= date - datetime.timedelta(1)
    response = OzonClient.GetFBSPostingList(from_date.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))
    for Posting in response:

        products = Posting.pop('products', None)



        if (delivery_method := Posting.pop('delivery_method', None)) is not None:
            delivery_method_, created = Ozon_FBS_DeliveryMethod.objects.update_or_create(
                id=delivery_method['id'],
                client_id=api_key,
                defaults={
                    **delivery_method,
                    'client_id': api_key,
                }
            )
            if created:
                pass
            else:
                delivery_method_.save()
        else:
            delivery_method_ = None




        analytics_data = Posting.pop('analytics_data', None)
        Customer = Posting.pop('customer', None)
        financial_data = Posting.pop('financial_data', None)

        available_actions = Posting.pop('available_actions', None)
        barcodes = Posting.pop('barcodes', None)
        cancellation = Posting.pop('cancellation', None)
        prr_option = Posting.pop('prr_option', None)
        requirements = Posting.pop('requirements', None)


        if (addressee := Posting.pop('addressee', None)) is not None:
            poluchatel = addressee['name']
        else:
            poluchatel = ''

        Posting_, created = Ozon_FBS_Posting.objects.update_or_create(
            posting_number=Posting['posting_number'],
            defaults={
                **Posting,
                'delivery_method':delivery_method_,
                'poluchatel':poluchatel,
                'client_id': api_key,
            }
        )
        if created:
            pass
        else:
            Posting_.save()

        for product in products:
            product.pop('mandatory_mark', None)
            products_, created = Ozon_FBS_Posting_Products.objects.update_or_create(
                offer_id=product['offer_id'],
                fbs_posting=Posting_,
                defaults={
                    **product,
                    'fbs_posting': Posting_,
                }
            )
            if created:
                pass
            else:
                products_.save()

        analytics_data_, created = Ozon_FBS_analytics_data.objects.update_or_create(
            fbs_posting=Posting_,
            defaults={
                **analytics_data,
                'fbs_posting': Posting_,
            }
        )
        if created:
            pass
        else:
            analytics_data_.save()

        if Customer:
            adresse = Customer.pop('address', None)
            Customer_, created = Ozon_FBS_Posting_Customer.objects.update_or_create(
                fbs_posting=Posting_,
                defaults={
                    **Customer,
                    'address_tail': adresse['address_tail'],
                    'city' : adresse['city'],
                    'comment' : adresse['comment'],
                    'country': adresse['country'],
                    'district': adresse['district'],
                    'latitude': adresse['latitude'],
                    'longitude' : adresse['longitude'],
                    'provider_pvz_code' : adresse['provider_pvz_code'],
                    'pvz_code' : adresse['pvz_code'],
                    'region' : adresse['region'],
                    'zip_code': adresse['zip_code'],
                    'fbs_posting': Posting_,
                }
            )
            if created:
                pass
            else:
                Customer_.save()

        for FinancialProduct in financial_data['products']:
            # Удаляем ключи 'actions' и 'picking' из FinancialProduct
            FinancialProduct.pop('actions', None)
            FinancialProduct.pop('picking', None)

            # Создаем отдельную переменную для item_services
            item_services = FinancialProduct.pop('item_services', None)

            # Теперь FinancialProduct не содержит этих ключей
            FinancialProduct_, created = OzonAllPostingFinancialProduct.objects.update_or_create(
                fbs_posting=Posting_,
                product_id=FinancialProduct['product_id'],
                defaults={
                    **FinancialProduct,
                    'marketplace_service_item_deliv_to_customer': item_services['marketplace_service_item_deliv_to_customer'],
                    'marketplace_service_item_direct_flow_trans': item_services['marketplace_service_item_direct_flow_trans'],
                    'marketplace_service_item_dropoff_ff': item_services['marketplace_service_item_dropoff_ff'],
                    'marketplace_service_item_dropoff_pvz': item_services['marketplace_service_item_dropoff_pvz'],
                    'marketplace_service_item_dropoff_sc': item_services['marketplace_service_item_dropoff_sc'],
                    'marketplace_service_item_fulfillment': item_services['marketplace_service_item_fulfillment'],
                    'marketplace_service_item_pickup': item_services['marketplace_service_item_pickup'],
                    'marketplace_service_item_return_after_deliv_to_customer': item_services['marketplace_service_item_return_after_deliv_to_customer'],
                    'marketplace_service_item_return_flow_trans': item_services['marketplace_service_item_return_flow_trans'],
                    'marketplace_service_item_return_not_deliv_to_customer': item_services['marketplace_service_item_return_not_deliv_to_customer'],
                    'marketplace_service_item_return_part_goods_customer': item_services['marketplace_service_item_return_part_goods_customer'],
                    'fbs_posting': Posting_,
                }
            )

            if created:
                pass
            else:
                FinancialProduct_.save()


def get_FBS_orders(filters):
    qs = Ozon_FBS_Posting.objects.all()
    if 'order_number' in filters:
        qs = qs.filter(order_number=filters['order_number'])

    if 'status' in filters:
        qs = qs.filter(status__in=filters['status'])

    if 'substatus' in filters:
        qs = qs.filter(substatus=filters['substatus'])

    if 'is_express' in filters:
        qs = qs.filter(is_express=filters['is_express'])

    if 'is_multibox' in filters:
        qs = qs.filter(is_multibox=filters['is_multibox'])

    if 'multi_box_qty' in filters:
        qs = qs.filter(multi_box_qty=filters['multi_box_qty'])

    if 'delivery_method' in filters:
        qs = qs.filter(delivery_method=filters['delivery_method'])

    if 'client_id' in filters:
        qs = qs.filter(client_id=filters['client_id'])

    if 'shipment_date__gte' in filters and 'shipment_date__lte' in filters:
        qs = qs.filter(shipment_date__gte=filters['shipment_date__gte'], shipment_date__lte=filters['shipment_date__lte'])

    if 'shipment_posting_date__gte' in filters:
        qs = qs.filter(shipment_posting_date__gte=filters['shipment_posting_date__gte'])
    if 'shipment_posting_date__lte' in filters:
        qs = qs.filter(shipment_posting_date__lte=filters['shipment_posting_date__lte'])


    if 'delivering_date__gte' in filters and 'delivering_date__lte' in filters:
        qs = qs.filter(delivering_date__gte=filters['delivering_date__gte'], delivering_date__lte=filters['delivering_date__lte'])


    if 'in_process_at__gte' in filters and 'in_process_at__lte' in filters:
        qs = qs.filter(in_process_at__gte=filters['in_process_at__gte'], in_process_at__lte=filters['in_process_at__lte'])

    qs = qs.prefetch_related('ozon_fbs_posting_products_set')
    return qs