from django import template
from marketplace.models import Ozon_Settings

register = template.Library()

@register.simple_tag
def get_ozon_shop(shop_id):
    return Ozon_Settings.objects.get(client_id=shop_id).name