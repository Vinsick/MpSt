from django.conf import settings
from django.db import models
from app.models import *
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from django.contrib.postgres.fields import ArrayField
from django.db.models import Sum
# Create your models here.

class Ozon_Settings(models.Model):
    client_id = models.CharField(max_length=30)
    client_key = models.CharField(max_length=50)
    name=models.CharField(max_length=50, null=True)

    def __str__(self):
        return (self.client_id)

class SMM_Settings(models.Model):
    shop_id = models.CharField(max_length=30)
    token = models.CharField(max_length=50)
    shop_id_api = models.CharField(max_length=50, null=True)

    def __str__(self):
        return (self.shop_id)

class Ozon_Status(models.Model):
    name = models.CharField(max_length=50)
    ru_name = models.CharField(max_length=50)

    def __str__(self):
        return (self.name)

class OzonCancellation(models.Model):
    cancel_reason_id = models.IntegerField(null=True)
    cancel_reason = models.TextField(null=True)
    cancellation_type = models.TextField(null=True)
    cancelled_after_ship = models.BooleanField(null=True)
    affect_cancellation_rating = models.BooleanField(null=True)
    cancellation_initiator = models.TextField(null=True)


class Ozon_Warehouse(models.Model):
    has_entrusted_acceptance = models.BooleanField(null=True, blank=True)
    is_rfbs = models.BooleanField(null=True, blank=True)
    name = models.CharField(max_length=200)
    warehouse_id = models.IntegerField(unique=True, primary_key=True)
    can_print_act_in_advance = models.BooleanField(null=True, blank=True)
    first_mile_type = models.TextField(blank=True, null=True)
    has_postings_limit = models.BooleanField(null=True, blank=True)
    is_karantin = models.BooleanField(null=True, blank=True)
    is_kgt = models.BooleanField(null=True, blank=True)
    is_timetable_editable = models.BooleanField(null=True, blank=True)
    min_postings_limit = models.IntegerField(null=True, blank=True)
    postings_limit = models.IntegerField(null=True, blank=True)
    min_working_days = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=200)
    working_days = models.TextField(blank=True, null=True)
    is_able_to_set_price = models.BooleanField()
    client_id = models.IntegerField(blank=True, default=0, null=True)

class OzonDeliveryMethod(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    warehouse_id = models.ForeignKey(Ozon_Warehouse, on_delete=models.SET_NULL, null=True)
    warehouse = models.CharField(max_length=255, null=True)
    tpl_provider_id = models.IntegerField(null=True)
    tpl_provider = models.CharField(max_length=255, null=True)

    def __str__(self):
        return (self.name)

class OzonAddress(models.Model):
    address_tail = models.TextField(null=True)
    city = models.CharField(max_length=255, null=True)
    comment = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    district = models.CharField(max_length=255, null=True)
    region = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=255, null=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    pvz_code = models.IntegerField(null=True)
    provider_pvz_code = models.CharField(max_length=255, null=True)

    def __str__(self):
        return (self.address_tail)

class OzonCustomer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    customer_email = models.EmailField(null=True)
    phone = models.CharField(max_length=40, null=True)
    address = models.ForeignKey(OzonAddress, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return (self.name)

class OzonProduct(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    offer_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    sku = models.BigIntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    currency_code = models.CharField(max_length=3, null=True, blank=True)
    mandatory_mark = models.TextField(blank=True, null=True)
    sebestoimist = models.DecimalField(max_digits=10, decimal_places=4, blank=True, default=0, null=True)


class OzonPosting(models.Model):
    posting_number = models.CharField(max_length=30, primary_key=True)
    order_id = models.BigIntegerField()
    order_number = models.CharField(max_length=30)
    status = models.CharField(max_length=50)
    delivery_method = models.ForeignKey(OzonDeliveryMethod, on_delete=models.SET_NULL, null=True)
    tracking_number = models.CharField(max_length=15, null=True)
    tpl_integration_type = models.CharField(max_length=255, null=True)
    in_process_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(null=True)
    shipment_date = models.DateTimeField(null=True)
    delivering_date = models.DateTimeField(null=True)
    products = models.ManyToManyField(OzonProduct, blank=True)
    cancellation = models.ForeignKey(OzonCancellation, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(OzonCustomer, null=True, on_delete=models.SET_NULL)
    substatus = models.CharField(max_length=255, null=True)
    mandatory_mark = models.TextField(blank=True, null=True)
    parent_posting_number = models.CharField(max_length=200, blank=True)
    prr_option = models.CharField(max_length=50, blank=True)
    multi_box_qty = models.IntegerField(blank=True, null=True)
    is_multibox = models.BooleanField(blank=True, null=True)
    substatus = models.CharField(max_length=200, blank=True)
    prr_option = models.CharField(max_length=200, blank=True)
    is_express = models.BooleanField(blank=True, null=True)
    addressee = models.CharField(max_length=200, blank=True)  # Addressee field is stored as a text
    barcodes = models.TextField(blank=True, null=True)
    financial_data = models.TextField(blank=True, null=True)
    additional_data = models.TextField(blank=True, null=True)
    cancel_reason_id = models.TextField(blank=True, null=True)
    analytics_data = models.TextField(blank=True, null=True)
    available_actions = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    client_id = models.IntegerField(blank=True, default=0, null=True)
    shipment_posting_date = models.DateTimeField(null=True)
    system_comment = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.shipment_posting_date:
            self.shipment_posting_date = self.shipment_date
        super().save(*args, **kwargs)

    def __str__(self):
        return (self.posting_number)
    
    def get_poluchatel(self):
        if self.customer is not None:
            poluchatel = self.customer
            return (poluchatel)
        else:
            return "Покупатель скрыт"
        
    def get_poluchatel_views(self):
        if self.customer is not None:
            poluchatel = self.customer
            return poluchatel.name
        else:
            return "Покупатель скрыт"       
    
    def get_products(self):
        products = self.products
        custumer = OzonCustomer.objects.get(id=products)
        return (custumer)
    
    def get_prosrochka_wtf(self):
        from datetime import datetime, timedelta
        now = timezone.now()
        ss_date = self.shipment_date

        if self.status == "awaiting_deliver":
            if (ss_date - timedelta(days=1)) < now:
                delta = ss_date - now
                
                # Получение дней, часов, минут и секунд из timedelta
                days, seconds = delta.days, delta.seconds
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = (seconds % 60)

                return str(f'Просрочка составляет: {days} д. {hours} ч. {minutes} м.')
                
        return str('Просрочки не найдены')

    def calculate_cena(self):
        total = 0
        for product in Ozon_Products.objects.filter(financial_data__ozon_posting=self):
            try:
                total += float(product.price)
            except ValueError:
                # Handle non-numeric values
                pass
        return total




class Ozon_Analytics_data(models.Model):
    ozon_posting = models.ForeignKey(OzonPosting, related_name='aaanalytics_data', on_delete=models.CASCADE)
    city = models.CharField(max_length=200, null=True)
    delivery_date_begin = models.DateTimeField(null=True)
    delivery_date_end = models.DateTimeField(null=True)
    delivery_type = models.CharField(max_length=200, null=True)
    is_legal = models.BooleanField(null=True)
    is_premium = models.BooleanField(null=True)
    payment_type_group_name = models.CharField(max_length=200, null=True)
    region = models.CharField(max_length=200, null=True)
    tpl_provider = models.CharField(max_length=200, null=True)
    tpl_provider_id = models.BigIntegerField(null=True)
    warehouse = models.CharField(max_length=200, null=True)
    warehouse_name = models.CharField(max_length=200, null=True, default=None)
    warehouse_id = models.BigIntegerField(null=True)



class Ozon_FinancialData(models.Model):
    ozon_posting = models.ForeignKey(OzonPosting, related_name='financialll_data', on_delete=models.CASCADE)
    cluster_from = models.CharField(max_length=255, null=True, blank=True)
    cluster_to = models.CharField(max_length=255, null=True, blank=True)

class Ozon_PostingServices(models.Model):
    financial_data = models.ForeignKey(Ozon_FinancialData, related_name='financial_posting_serv', on_delete=models.CASCADE)
    marketplace_service_item_deliv_to_customer = models.FloatField(null=True, blank=True)
    marketplace_service_item_direct_flow_trans = models.FloatField(null=True, blank=True)
    marketplace_service_item_dropoff_ff = models.FloatField(null=True, blank=True)
    marketplace_service_item_dropoff_pvz = models.FloatField(null=True, blank=True)
    marketplace_service_item_dropoff_sc = models.FloatField(null=True, blank=True)
    marketplace_service_item_fulfillment = models.FloatField(null=True, blank=True)
    marketplace_service_item_pickup = models.FloatField(null=True, blank=True)
    marketplace_service_item_return_after_deliv_to_customer = models.FloatField(null=True, blank=True)
    marketplace_service_item_return_flow_trans = models.FloatField(null=True, blank=True)
    marketplace_service_item_return_not_deliv_to_customer = models.FloatField(null=True, blank=True)
    marketplace_service_item_return_part_goods_customer = models.FloatField(null=True, blank=True)

class Ozon_Products(models.Model):
    financial_data = models.ForeignKey(Ozon_FinancialData,  related_name='financialll_data_product', on_delete=models.CASCADE)
    actions = models.CharField(max_length=255, null=True, blank=True)
    currency_code = models.CharField(max_length=255, null=True, blank=True)
    client_price = models.CharField(max_length=255, null=True, blank=True)
    commission_amount = models.FloatField(null=True, blank=True)
    commission_percent = models.IntegerField(null=True, blank=True)
    commissions_currency_code = models.CharField(max_length=255, null=True, blank=True)
    old_price = models.FloatField(null=True, blank=True)
    payout = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    product_id = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    total_discount_percent = models.FloatField(null=True, blank=True)
    total_discount_value = models.FloatField(null=True, blank=True)

class Ozon_ProductList(models.Model):
    product_id = models.IntegerField(null=True, blank=True, unique=True)
    offer_id = models.CharField(max_length=255, null=True, blank=True)
    client_id = models.IntegerField(blank=True, default=0, null=True)
    sku = models.IntegerField(null=True, blank=True)

class Ozon_ItemServices(models.Model):
    product = models.ForeignKey(Ozon_Products, related_name='ozonitemservices', on_delete=models.CASCADE)
    marketplace_service_item_deliv_to_customer = models.FloatField(null=True, blank=True)
    marketplace_service_item_direct_flow_trans = models.FloatField(null=True, blank=True)
    marketplace_service_item_dropoff_ff = models.FloatField(null=True, blank=True)
    marketplace_service_item_dropoff_pvz = models.FloatField(null=True, blank=True)
    marketplace_service_item_dropoff_sc = models.FloatField(null=True, blank=True)
    marketplace_service_item_fulfillment = models.FloatField(null=True, blank=True)
    marketplace_service_item_pickup = models.FloatField(null=True, blank=True)
    marketplace_service_item_return_after_deliv_to_customer = models.FloatField(null=True, blank=True)
    marketplace_service_item_return_flow_trans = models.FloatField(null=True, blank=True)
    marketplace_service_item_return_not_deliv_to_customer = models.FloatField(null=True, blank=True)
    marketplace_service_item_return_part_goods_customer = models.FloatField(null=True, blank=True)

class Characteristic(models.Model):
    name = models.CharField('Название', max_length=200)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField('Название категории', max_length=200)

    def __str__(self):
        return self.name

class MpProduct(models.Model):
    artikul = models.CharField('Артикул', max_length=200, null=True)
    category = models.ForeignKey(Category, verbose_name='Категория товара', on_delete=models.SET_NULL, null=True)
    characteristics = models.ManyToManyField(Characteristic, through='ProductCharacteristic', related_name='products')
    kol = models.IntegerField(null=True, blank=True, default=1)
    sebestoimost = models.DecimalField('Себестоимость', max_digits=10, decimal_places=2, null=True, default=0)

    def __str__(self):
        return self.artikul or "Без артикула"

    def get_characteristic_value_true(self, characteristic):
        # Получаем экземпляр Characteristic, связанный с текущим MpProduct и заданной характеристикой
        char = Characteristic.objects.get(name=characteristic)
        product_characteristic = self.productcharacteristic_set.filter(characteristic=char, product=self).first()

        if product_characteristic:
            return product_characteristic.value
        else:
            return None

    def get_characteristic_value(self, characteristic):
        # Получаем экземпляр ProductCharacteristic, связанный с текущим MpProduct и заданной характеристикой
        char = Characteristic.objects.get(name=characteristic)
        product_characteristic = self.productcharacteristic_set.filter(characteristic=char, product=self)

        if product_characteristic:
            return f"{product_characteristic}"
        else:
            return f""

    def get_characteristics_table(self, count=1):
        if self.category.__str__() == "Кокон":
            characteristics = self.characteristics.all()
            kokon=''
            stoika=''
            kreplenie=''
            podushka=''
            reklainer=''
            podgolovnik=''
            podarok=''

            for characteristic in characteristics:
                product_characteristic = ProductCharacteristic.objects.get(product=self, characteristic=characteristic)

                if characteristic.name == "Форма кокона":
                    kokon += f'<strong>{product_characteristic.value} </strong>'
                if characteristic.name == "Плетение":
                    kokon += f'<strong> {product_characteristic.value} </strong>'
                if characteristic.name == "Цвет плетения":
                    kokon += f'<strong> {product_characteristic.value} </strong>'



                if characteristic.name == "Дуга":
                    stoika += f'Дуга: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Основание":
                    stoika += f'Основание: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет основания":
                    stoika += f'Цвет: <strong>{product_characteristic.value}</strong><br>'



                if characteristic.name == "Крепление":
                    kreplenie += f'Крепление: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Чехлы на крепление":
                    kreplenie += f'Чехлы: <strong>{product_characteristic.value}</strong><br>'



                if characteristic.name == "Форма подушки":
                    podushka += f'Форма: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Ткань подушки":
                    podushka += f'Ткань: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет подушки":
                    podushka += f'Цвет: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Наполнитель подушки":
                    podushka += f'Наполнитель: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Форма реклайнера":
                    reklainer += f'Форма: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет реклайнера":
                    reklainer += f'Цвет: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "подушки реклайнера":
                    reklainer += f'Ткань подушки: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет подушки реклайнера":
                    reklainer += f'Цвет подушки: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Ткань подголовника":
                    podgolovnik += f'Ткань: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет подголовника":
                    podgolovnik += f'Цвет: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Подарок":
                    podarok = f'<strong>{product_characteristic.value}</strong>'

            html = '<div class="table-responsive">'
            html += '<table class="table table-bordered">'
            html += '<thead class="text-center"><tr><td><strong>Кокон</strong></td><td><strong>Стойка</strong></td><td><strong>Крепление</strong></td><td><strong>Подушка</strong></td>'
            if reklainer != '':
                html+='<td><strong>Реклайнер</strong></td>'
            if podgolovnik != '':
                html+='<td><strong>Подголовник</strong></td>'
            if count > 1:
                html += f'<td><strong>Количество<strong></td>'

            html += '</tr><thead><tbody><tr>'

            html += f'<td>{kokon}</td>'
            html += f'<td>{stoika}</td>'
            html += f'<td>{kreplenie}</td>'
            html += f'<td>{podushka}</td>'
            if reklainer != '':
                html += f'<td>{reklainer}</td>'
            if podgolovnik != '':
                html += f'<td>{podgolovnik}</td>'
            if count > 1:
                html += f'<td>{count}</td>'

            html += '</tr></tbody>'
            html += '</table>'
            if podarok != '':
                html += f'<p>Подарок: {podarok}</p>'
            html += '</div>'
            return html
        elif self.category.__str__() == "Стул":
            characteristics = self.characteristics.all()
            forma=''
            karkas=''
            pokritie=''
            sidenie=''
            kolvo=''
            podarok=''
            
            for characteristic in characteristics:
                product_characteristic = ProductCharacteristic.objects.get(product=self, characteristic=characteristic)

                if characteristic.name == "Форма стула":
                    forma += f'Форма: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Форма ножек":
                    karkas += f'Ножки: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Разбор/цельные":
                    karkas += f'Тип: <strong>{product_characteristic.value}</strong><br>'


                if characteristic.name == "Покрытие ножек":
                    pokritie += f'Покрытие: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет ножек":
                    pokritie += f'Цвет: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Ткань обивки":
                    sidenie += f'Ткань: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет обивки":
                    sidenie += f'Цвет: <strong>{product_characteristic.value}</strong><br>'
                    

                if characteristic.name == "Количество стульев":
                    kok = int(product_characteristic.value) * int(count)
                    kolvo += f'<strong>{kok}</strong><br>'




            html = '<div class="table-responsive">'
            html += '<table class="table table-bordered">'
            html += '<thead class="text-center"><tr><td><strong>Форма</strong></td><td><strong>Каркас</strong></td><td><strong>Покрытие</strong></td><td><strong>Сиденье</strong></td><td><strong>Количество</strong></td>'

            html += '</tr><thead><tbody><tr>'

            html += f'<td>{forma}</td>'
            html += f'<td>{karkas}</td>'
            html += f'<td>{pokritie}</td>'
            html += f'<td>{sidenie}</td>'
            html += f'<td>{kolvo}</td>'



            html += '</tr></tbody>'
            html += '</table>'

            html += '</div>'
            return html
        elif self.category.__str__() == "Плетеный стул":
            characteristics = self.characteristics.all()
            nazvanie=''
            nojki=''
            poduska=''

            for characteristic in characteristics:
                product_characteristic = ProductCharacteristic.objects.get(product=self, characteristic=characteristic)

                if characteristic.name == "Название плетенного стула":
                    nazvanie += f'<strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет плетенной мебели":
                    nazvanie += f'Цвет: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Ножки плетенного стула":
                    nojki += f'Ножки: <strong>{product_characteristic.value}</strong><br>'


                if characteristic.name == "Форма подушки":
                    poduska += f'Форма: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Ткань подушки":
                    poduska += f'Ткань: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет подушки":
                    poduska += f'Цвет: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Наполнитель подушки":
                    poduska += f'Наполнитель: <strong>{product_characteristic.value}</strong><br>'




            html = '<div class="table-responsive">'
            html += '<table class="table table-bordered">'
            html += '<thead class="text-center"><tr><td><strong>Название</strong></td><td><strong>Ножки</strong></td><td><strong>Подушка</strong></td>'
            if count > 1:
                html += f'<td><strong>Количество<strong></td>'
            html += '</tr><thead><tbody><tr>'

            html += f'<td>{nazvanie}</td>'
            html += f'<td>{nojki}</td>'
            html += f'<td>{poduska}</td>'
            if count > 1:
                html += f'<td>{count}</td>'


            html += '</tr></tbody>'
            html += '</table>'

            html += '</div>'
            return html
        elif self.category.__str__() == "Подставка под елку":
            characteristics = self.characteristics.all()
            nazvanie=''
            cvet=''
            osob=''
            diam=''

            for characteristic in characteristics:
                product_characteristic = ProductCharacteristic.objects.get(product=self, characteristic=characteristic)

                if characteristic.name == "Цвет ротанга для подставки под елку":
                    cvet += f'Цвет: <strong>{product_characteristic.value}</strong><br>'


                if characteristic.name == "Особенности подставки под елку":
                    osob += f'<strong>{product_characteristic.value}</strong><br>'

                if characteristic.id == 122:
                    diam += f'<strong>{str(product_characteristic.value)}</strong><br>'




            html = '<div class="table-responsive">'
            html += '<table class="table table-bordered">'
            html += '<thead class="text-center"><tr><td><strong>Название</strong></td><td><strong>Цвет</strong></td><td><strong>Особенности</strong></td><td><strong>Диаметр</strong></td>'
            if count > 1:
                html += f'<td><strong>Количество<strong></td>'
            html += '</tr><thead><tbody><tr>'

            html += f'<td><strong>{self.category.__str__()}</strong></td>'
            html += f'<td>{cvet}</td>'
            html += f'<td>{osob}</td>'
            html += f'<td>{diam}</td>'
            if count > 1:
                html += f'<td>{count}</td>'


            html += '</tr></tbody>'
            html += '</table>'

            html += '</div>'
            return html
        elif self.category.__str__() == "Папасан":
            characteristics = self.characteristics.all()
            nazvanie=''
            pletenie=''
            poduska=''
            podg = ''

            for characteristic in characteristics:
                product_characteristic = ProductCharacteristic.objects.get(product=self, characteristic=characteristic)

                if characteristic.name == "Название папасана":
                    nazvanie += f'<strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет каркаса папасана":
                    nazvanie += f'Цвет: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Плетение":
                    pletenie += f'Плетение: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет каркаса папасана":
                    pletenie += f'Цвет: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Форма подушки":
                    poduska += f'Форма: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Ткань подушки":
                    poduska += f'Ткань: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет подушки":
                    poduska += f'Цвет: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Наполнитель подушки":
                    poduska += f'Наполнитель: <strong>{product_characteristic.value}</strong><br>'

                if characteristic.name == "Ткань подголовника":
                    podg += f'Ткань: <strong>{product_characteristic.value}</strong><br>'
                if characteristic.name == "Цвет подголовника":
                    podg += f'Цвет: <strong>{product_characteristic.value}</strong><br>'



            html = '<div class="table-responsive">'
            html += '<table class="table table-bordered">'
            html += '<thead class="text-center"><tr><td><strong>Название</strong></td><td><strong>Плетение</strong></td><td><strong>Подушка</strong></td><td><strong>Подголовник</strong></td>'
            if count > 1:
                html += f'<td><strong>Количество<strong></td>'

            html += '</tr><thead><tbody><tr>'

            html += f'<td>{nazvanie}</td>'
            html += f'<td>{pletenie}</td>'
            html += f'<td>{poduska}</td>'
            html += f'<td>{podg}</td>'
            if count > 1:
                html += f'<td>{count}</td>'


            html += '</tr></tbody>'
            html += '</table>'

            html += '</div>'
            return html
        else:
            characteristics = self.characteristics.all()
            cvet=''

            for characteristic in characteristics:
                product_characteristic = ProductCharacteristic.objects.get(product=self, characteristic=characteristic)
                cvet += f'{characteristic.name}: <strong>{product_characteristic.value}</strong><br>'

            html = '<div class="table-responsive">'
            html += '<table class="table table-bordered">'
            html += '<thead class="text-center"><tr><td><strong>Категория</strong></td><td><strong>Характеристики</strong></td>'
            if count > 1:
                html += f'<td><strong>Количество<strong></td>'
            html += '</tr><thead><tbody><tr>'

            html += f'<td><strong>{self.category.__str__()}</strong></td>'
            html += f'<td>{cvet}</td>'
            if count > 1:
                html += f'<td>{count}</td>'



            html += '</tr></tbody>'
            html += '</table>'

            html += '</div>'
            return html


class ProductCharacteristic(models.Model):
    product = models.ForeignKey(MpProduct, verbose_name='Товар', on_delete=models.CASCADE)
    characteristic = models.ForeignKey(Characteristic, verbose_name='Характеристика', on_delete=models.CASCADE)
    value = models.CharField('Значение', max_length=200)

    def __str__(self):
        return f"{self.characteristic.name}: {self.value}"


class YaOrder(models.Model):
    id_order = models.IntegerField(null=True)
    status = models.CharField(max_length=50, null=True)
    substatus = models.CharField(max_length=50, null=True)
    creation_date = models.DateTimeField(null=True)
    items_total = models.IntegerField(null=True)
    total = models.IntegerField(null=True)
    delivery_total = models.IntegerField(null=True)
    subsidy_total = models.IntegerField(null=True)
    total_with_subsidy = models.IntegerField(null=True)
    buyer_items_total = models.IntegerField(null=True)
    buyer_total = models.IntegerField(null=True)
    buyer_items_total_before_discount = models.IntegerField(null=True)
    buyer_total_before_discount = models.IntegerField(null=True)
    payment_type = models.CharField(max_length=50, null=True)
    payment_method = models.CharField(max_length=50, null=True)
    fake = models.BooleanField(null=True)
    id_shop = models.CharField(max_length=255, null=True)
    shipmentDate = models.DateTimeField(null=True)
    shipment_posting_date = models.DateTimeField(null=True)
    system_comment = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.shipment_posting_date:
            self.shipment_posting_date = self.shipmentDate
        super().save(*args, **kwargs)


class YaItem(models.Model):
    ya_order = models.ForeignKey(YaOrder, related_name='items', on_delete=models.CASCADE)
    id_item = models.IntegerField(null=True)
    feed_id = models.IntegerField(null=True)
    offer_id = models.CharField(max_length=255, null=True)
    feed_category_id = models.CharField(max_length=255, null=True)
    offer_name = models.CharField(max_length=255, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    buyer_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    buyer_price_before_discount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_before_discount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    count = models.IntegerField(null=True)
    vat_status = models.CharField(max_length=50, null=True)
    shop_sku = models.CharField(max_length=255, null=True)
    subsidy = models.IntegerField(null=True)
    partner_warehouse_id = models.CharField(max_length=255, null=True)


class YaDelivery(models.Model):
    ya_order = models.ForeignKey(YaOrder,related_name='delivery', on_delete=models.CASCADE)
    id_delivery = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, null=True)
    service_name = models.CharField(max_length=255, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    delivery_partner_type = models.CharField(max_length=255, null=True)
    from_date = models.DateField(null=True)
    to_date = models.DateField(null=True)
    from_time = models.TimeField(null=True)
    to_time = models.TimeField(null=True)
    region_name = models.CharField(max_length=255, null=True)
    city_name = models.CharField(max_length=255, null=True, blank=True)
    region_type = models.CharField(max_length=255, null=True)
    city_type = models.CharField(max_length=255, null=True, blank=True)


class YaBuyer(models.Model):
    ya_order = models.OneToOneField(YaOrder, related_name='buyer', on_delete=models.CASCADE)
    last_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=50, null=True)





class SMMGoodsData(models.Model):
    name = models.CharField(max_length=255)
    category_name = models.CharField(max_length=255)
    is_delivery = models.BooleanField(null=True) 
    is_digital_mark_required = models.BooleanField(null=True) 

class SMMCustomer(models.Model):
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=400)

class SMMShipment(models.Model):
    shipmentId = models.CharField(max_length=255)
    orderCode = models.CharField(max_length=255, null=True)
    confirmedTimeLimit = models.CharField(max_length=255)
    packingTimeLimit = models.CharField(max_length=255)
    shippingTimeLimit = models.CharField(max_length=255)
    shipmentDateFrom = models.DateTimeField()
    shipmentDateTo = models.DateTimeField()
    deliveryId = models.CharField(max_length=255)
    shipmentDateShift = models.BooleanField()
    shipmentIsChangeable = models.BooleanField()
    customerFullName = models.CharField(max_length=255)
    customerAddress = models.CharField(max_length=400)
    shippingPoint = models.CharField(max_length=255)
    creationDate = models.DateTimeField()
    packingDate = models.DateTimeField(null=True)
    deliveryDate = models.DateTimeField()
    deliveryDateFrom = models.DateTimeField()
    deliveryDateTo = models.DateTimeField()
    deliveryMethodId = models.CharField(max_length=255)
    depositedAmount = models.IntegerField()
    status = models.CharField(max_length=255, null=True)
    shipment_posting_date = models.DateTimeField(null=True)
    system_comment = models.TextField(blank=True, null=True)
    id_shop_api = models.CharField(max_length=30, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.shipment_posting_date:
            self.shipment_posting_date = self.shipmentDateFrom
        super().save(*args, **kwargs)

    def calculate_cena(self):
        total = 0
        for product in SMMItem.objects.filter(shipment=self):
            try:
                total += float(product.finalPrice)
            except ValueError:
                # Handle non-numeric values
                pass
        return total

    def shipment_date_from_formatted(self):
        dt = datetime.strptime(self.shipmentDateFrom, '%Y-%m-%dT%H:%M:%S%z')
        return dt.strftime('%d.%m.%Y')

    def creation_date_formatted(self):
        dt = datetime.strptime(self.creationDate, '%Y-%m-%dT%H:%M:%S%z')
        return dt.strftime('%d.%m.%Y')
    
class SMMItem(models.Model):
    shipment = models.ForeignKey(SMMShipment,  related_name='items', on_delete=models.CASCADE)
    itemIndex = models.CharField(max_length=255)
    status = models.CharField(max_length=255, null=True)
    subStatus = models.CharField(max_length=255, blank=True, null=True)
    price = models.IntegerField()
    finalPrice = models.IntegerField()
    quantity = models.IntegerField()
    offerId = models.CharField(max_length=255)
    goodsId = models.CharField(max_length=255)
    goodsData = models.ForeignKey(SMMGoodsData, on_delete=models.CASCADE)
    boxIndex = models.CharField(max_length=255, null=True)

class SMMDiscount(models.Model):
    item = models.ForeignKey(SMMItem, on_delete=models.CASCADE)
    discountType = models.CharField(max_length=255)
    discountDescription = models.CharField(max_length=255)
    discountAmount = models.IntegerField()


class SMMEvent(models.Model):
    smm_item = models.ForeignKey(SMMItem, related_name='smm_events', on_delete=models.CASCADE)
    eventDate = models.DateTimeField(null=True)
    eventName = models.CharField(max_length=255, null=True)
    eventValue = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.eventName} at {self.eventDate}"