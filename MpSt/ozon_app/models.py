from django.db import models

# Create your models here.
class OzonSettings(models.Model):
    client_id = models.CharField(max_length=30)
    client_key = models.CharField(max_length=50)
    name=models.CharField(max_length=50, null=True)


class OzonWarehouse(models.Model):
    warehouse_id = models.IntegerField(primary_key=True)  # Идентификатор склада
    name = models.CharField(max_length=255)  # Название склада
    has_entrusted_acceptance = models.BooleanField()  # Признак доверительной приёмки
    is_rfbs = models.BooleanField()  # Признак работы склада по схеме rFBS
    can_print_act_in_advance = models.BooleanField()  # Возможность печати акта приёма-передачи заранее
    dropoff_point_id = models.CharField(max_length=255, null=True, blank=True)  # Идентификатор DropOff-точки
    dropoff_timeslot_id = models.IntegerField(null=True, blank=True)  # Идентификатор временного слота для DropOff
    first_mile_is_changing = models.BooleanField()  # Признак, что настройки склада обновляются
    first_mile_type = models.CharField(max_length=255)  # Тип первой мили — DropOff или Pickup
    has_postings_limit = models.BooleanField()  # Признак наличия лимита минимального количества заказов
    is_karantin = models.BooleanField()  # Признак, что склад не работает из-за карантина
    is_kgt = models.BooleanField()  # Признак, что склад принимает крупногабаритные товары
    is_timetable_editable = models.BooleanField()  # Признак, что можно менять расписание работы складов
    min_postings_limit = models.IntegerField()  # Минимальное значение лимита — количество заказов, которые можно привезти в одной поставке
    postings_limit = models.IntegerField()  # Значение лимита. -1, если лимита нет
    min_working_days = models.IntegerField()  # Количество рабочих дней склада
    status = models.CharField(max_length=255)  # Статус склада
    working_days = models.CharField(max_length=255)  # Рабочие дни склада
    is_able_to_set_price = models.BooleanField(null=True)  # Признак, что настройки склада обновляются
    client_id = models.ForeignKey(OzonSettings, on_delete=models.SET_NULL, null=True)


class OzonDeliveryMethod(models.Model):
    company_id = models.BigIntegerField()
    created_at = models.DateTimeField()
    cutoff = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    provider_id = models.BigIntegerField()
    status = models.CharField(max_length=255, choices=[
        ('NEW', 'Создан'),
        ('EDITED', 'Редактируется'),
        ('ACTIVE', 'Активный'),
        ('DISABLED', 'Неактивный'),
    ])
    template_id = models.BigIntegerField()
    updated_at = models.DateTimeField()
    warehouse_id = models.ForeignKey(OzonWarehouse, on_delete=models.SET_NULL, null=True)
    client_id = models.ForeignKey(OzonSettings, on_delete=models.SET_NULL, null=True)



class OzonFBOPosting(models.Model):
    posting_number = models.CharField(max_length=200, primary_key=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    delivery_type = models.CharField(max_length=200, null=True, blank=True)
    is_legal = models.BooleanField()
    is_premium = models.BooleanField()
    payment_type_group_name = models.CharField(max_length=200, null=True, blank=True)
    region = models.CharField(max_length=200, null=True, blank=True)
    warehouse_id = models.CharField(max_length=200, null=True, blank=True)
    warehouse_name = models.CharField(max_length=200, null=True, blank=True)
    cancel_reason_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField()
    in_process_at = models.DateTimeField(null=True, blank=True)
    order_id = models.BigIntegerField()
    order_number = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    client_id = models.ForeignKey(OzonSettings, on_delete=models.SET_NULL, null=True)

class OzonProduct(models.Model):
    client_id = models.ForeignKey(OzonSettings, on_delete=models.SET_NULL, null=True)
    product_id = models.IntegerField() 
    offer_id = models.CharField(max_length=255, null=True, blank=True)
    is_fbo_visible = models.BooleanField(null=True)
    is_fbs_visible = models.BooleanField(null=True)
    archived = models.BooleanField(null=True)
    is_discounted = models.BooleanField(null=True)



class Ozon_FBO_Posting_Products(models.Model):
    id = models.IntegerField(primary_key=True)
    digital_codes = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    offer_id = models.CharField(max_length=200)
    currency_code = models.CharField(max_length=200, choices=[
        ('RUB', 'Российский рубль'),
        ('BYN', 'Белорусский рубль'),
        ('KZT', 'Тенге'),
        ('EUR', 'Евро'),
        ('USD', 'Доллар США'),
        ('CNY', 'Юань'),
    ])
    price = models.FloatField()
    quantity = models.IntegerField()
    sku = models.IntegerField()
    fbo_postings = models.ForeignKey(OzonFBOPosting, on_delete=models.SET_NULL, null=True)





class Ozon_FBS_DeliveryMethod(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    tpl_provider = models.CharField(max_length=255)
    tpl_provider_id = models.BigIntegerField()
    warehouse = models.CharField(max_length=255)
    warehouse_id = models.BigIntegerField()
    client_id = models.ForeignKey(OzonSettings, on_delete=models.SET_NULL, null=True)

class Ozon_FBS_Posting(models.Model):
    posting_number = models.CharField(max_length=200, primary_key=True)
    poluchatel=models.CharField(max_length=255, blank=True)
    delivering_date = models.DateTimeField(null=True)
    in_process_at = models.DateTimeField()
    is_express = models.BooleanField()
    is_multibox = models.BooleanField()
    multi_box_qty = models.IntegerField()
    order_id = models.BigIntegerField()
    order_number = models.CharField(max_length=255)
    parent_posting_number = models.CharField(max_length=255)
    shipment_date = models.DateTimeField()
    status = models.CharField(max_length=255)
    substatus = models.CharField(max_length=255)
    tpl_integration_type = models.CharField(max_length=255)
    tracking_number = models.CharField(max_length=255, null=True)
    delivery_method = models.ForeignKey(Ozon_FBS_DeliveryMethod, on_delete=models.SET_NULL, null=True)
    client_id = models.ForeignKey(OzonSettings, on_delete=models.SET_NULL, null=True)
    shipment_posting_date = models.DateTimeField(null=True)
    system_comment = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.shipment_posting_date:
            self.shipment_posting_date = self.shipment_date
        super().save(*args, **kwargs)

    @staticmethod
    def translateStatus(status):
        translatedStatus = status
        className = 'badge-secondary'

        status_dict = {
            'acceptance_in_progress': ('Идёт приёмка', 'badge-primary'),
            'arbitration': ('Арбитраж', 'badge-danger'),
            'awaiting_approve': ('Ожидает подтверждения', 'badge-warning'),
            'awaiting_deliver': ('Ожидает отгрузки', 'badge-info'),
            'awaiting_packaging': ('Ожидает упаковки', 'badge-light'),
            'awaiting_registration': ('Ожидает регистрации', 'badge-secondary'),
            'awaiting_verification': ('Создано', 'badge-success'),
            'cancelled': ('Отменено', 'badge-danger'),
            'cancelled_from_split_pending': ('Отменено', 'badge-danger'),
            'client_arbitration': ('Клиентский арбитраж доставки', 'badge-danger'),
            'delivering': ('Доставляется', 'badge-dark'),
            'driver_pickup': ('У водителя', 'badge-info'),
            'not_accepted': ('Не принят на сортировочном центре', 'badge-warning'),
            'sent_by_seller': ('Отправлено продавцом', 'badge-success'),
            'delivered': ('Доставлено', 'badge-success')
        }

        if status in status_dict:
            translatedStatus, className = status_dict[status]

        return {
            'translatedStatus': translatedStatus,
            'className': className
        }

    def get_status_html(self):
        translated = self.translateStatus(self.status)
        return '<span class="badge badge-pill {}">{}</span>'.format(translated['className'], translated['translatedStatus'])
        
class Ozon_FBS_Posting_Products(models.Model):
    name = models.CharField(max_length=255)
    offer_id = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    quantity = models.IntegerField()
    sku = models.BigIntegerField()
    currency_code = models.CharField(max_length=3, choices=[
        ('RUB', 'Российский рубль'),
        ('BYN', 'Белорусский рубль'),
        ('KZT', 'Тенге'),
        ('EUR', 'Евро'),
        ('USD', 'Доллар США'),
        ('CNY', 'Юань'),
    ])
    fbs_posting = models.ForeignKey(Ozon_FBS_Posting, on_delete=models.SET_NULL, null=True)



class Ozon_FBS_analytics_data(models.Model):
    city = models.CharField(max_length=200)
    delivery_date_begin = models.DateTimeField()
    delivery_date_end = models.DateTimeField()
    delivery_type = models.CharField(max_length=200)
    is_legal = models.BooleanField()
    is_premium = models.BooleanField()
    payment_type_group_name = models.CharField(max_length=200)
    region = models.CharField(max_length=200)
    tpl_provider = models.CharField(max_length=200)
    tpl_provider_id = models.BigIntegerField()
    warehouse = models.CharField(max_length=200)
    warehouse_id = models.BigIntegerField()
    fbs_posting = models.ForeignKey(Ozon_FBS_Posting, on_delete=models.SET_NULL, null=True)

class Ozon_FBS_Posting_Customer(models.Model):
    address_tail = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    comment = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    provider_pvz_code = models.CharField(max_length=255, blank=True)
    pvz_code = models.IntegerField(null=True, blank=True)
    region = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=255, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    fbs_posting = models.ForeignKey(Ozon_FBS_Posting, on_delete=models.SET_NULL, null=True)


class OzonAllPostingFinancialProduct(models.Model):
    CURRENCY_CHOICES = (
        ('RUB', 'Российский рубль'),
        ('BYN', 'Белорусский рубль'),
        ('KZT', 'Тенге'),
        ('EUR', 'Евро'),
        ('USD', 'Доллар США'),
        ('CNY', 'Юань'),
    )

    currency_code = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    client_price = models.CharField(max_length=255)
    commission_amount = models.FloatField()
    commission_percent = models.IntegerField()
    commissions_currency_code = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    marketplace_service_item_deliv_to_customer = models.FloatField()
    marketplace_service_item_direct_flow_trans = models.FloatField()
    marketplace_service_item_dropoff_ff = models.FloatField()
    marketplace_service_item_dropoff_pvz = models.FloatField()
    marketplace_service_item_dropoff_sc = models.FloatField()
    marketplace_service_item_fulfillment = models.FloatField()
    marketplace_service_item_pickup = models.FloatField()
    marketplace_service_item_return_after_deliv_to_customer = models.FloatField()
    marketplace_service_item_return_flow_trans = models.FloatField()
    marketplace_service_item_return_not_deliv_to_customer = models.FloatField()
    marketplace_service_item_return_part_goods_customer = models.FloatField()
    old_price = models.FloatField()
    payout = models.FloatField()
    price = models.FloatField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()
    total_discount_percent = models.FloatField()
    total_discount_value = models.FloatField()
    fbo_posting = models.ForeignKey(OzonFBOPosting, on_delete=models.SET_NULL, null=True)
    fbs_posting = models.ForeignKey(Ozon_FBS_Posting, on_delete=models.SET_NULL, null=True)
