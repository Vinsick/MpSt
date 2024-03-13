from django import template
from django.db.models import ObjectDoesNotExist

register = template.Library()

@register.simple_tag
def get_ozon_product_table(artikul, count=1):
    try:
        try:
            return f"{artikul}"
            
        except ObjectDoesNotExist:
            return f"Артикул {artikul} не найден в базе артиклов"
        return product.get_characteristics_table(count=count)
    except ObjectDoesNotExist:
        return f"Неизвестная ошибка с {artikul}"