from django import template

register = template.Library()

@register.filter
def ozon_warehouse_status_translate(value):
    status_translations = {
        'new': 'Активируется',
        'created': '<span class="badge badge-primary">Активный</span>',
        'disabled': '<span class="badge badge-dark">В архиве</span>',
        'blocked': '<span class="badge badge-danger">Заблокирован</span>',
        'disabled_due_to_limit': '<span class="badge badge-light">На паузе</span>',
        'error': '<span class="badge badge-danger">Ошибка</span>',
    }
    return status_translations.get(value, value)