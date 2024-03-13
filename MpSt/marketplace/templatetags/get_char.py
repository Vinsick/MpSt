from django import template
from marketplace.models import MpProduct, Characteristic

register = template.Library()

@register.simple_tag
def get_char(product_id, characteristic_name):
    try:
        product = MpProduct.objects.get(id=product_id)
        characteristic = Characteristic.objects.get(name=characteristic_name)
        return product.get_characteristic_value(characteristic)
    except (MpProduct.DoesNotExist, Characteristic.DoesNotExist):
        return ""