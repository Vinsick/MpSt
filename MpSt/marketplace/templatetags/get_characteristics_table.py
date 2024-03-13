from django import template
from marketplace.views import Ozon
from marketplace.models import *
from django.db.models import ObjectDoesNotExist

register = template.Library()

@register.simple_tag
def get_characteristics_table(artikul, count=1, client_id=None):
    try:
        get = Ozon_ProductList.objects.get(product_id=artikul)

        try:
            product = MpProduct.objects.get(artikul=get.offer_id)
            
        except ObjectDoesNotExist:
            return f"Артикул {get.offer_id} не найден в базе артиклов"
        return product.get_characteristics_table(count=count)
    except ObjectDoesNotExist:
        print(artikul)
        tt = Ozon()
        tt.Prod_list_getIS(offer_id=artikul)
        return f"Id Товара ({artikul}) не существует в товарной базе Ozon"