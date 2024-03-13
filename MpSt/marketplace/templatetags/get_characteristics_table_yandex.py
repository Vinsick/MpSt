from django import template
from marketplace.views import Ozon
from marketplace.models import *
from django.db.models import ObjectDoesNotExist

register = template.Library()

@register.simple_tag
def get_characteristics_table_yandex(artikul, count=1, client_id=None):
    try:
        try:
            product = MpProduct.objects.get(artikul=artikul)
            
        except ObjectDoesNotExist:
            return f"Артикул {artikul} не найден в базе артиклов"
        return product.get_characteristics_table(count=count)
    except ObjectDoesNotExist:
        return f"Неизвестная ошибка с {artikul}"