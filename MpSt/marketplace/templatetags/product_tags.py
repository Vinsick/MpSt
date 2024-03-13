from django import template
from marketplace.models import *

register = template.Library()

@register.simple_tag
def get_mp_product(offer_id):
    return MpProduct.objects.prefetch_related('characteristics').get(artikul=offer_id)