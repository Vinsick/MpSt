from django import forms
from django.forms import formset_factory
from .models import MpProduct, ProductCharacteristic, Characteristic, Category
from django.utils.safestring import mark_safe
from django.utils.html import format_html

# Стили для детских элементов формы
CHILD_FRIENDLY_STYLES = {
    'class': 'form-control child-friendly-input', 
    'style': 'border: 2px solid #a1daf7; border-radius: 15px; font-size: 16px;'
}

# Использование ярких иконок
ICON_ARTIKUL = '<i class="fas fa-puzzle-piece" style="color: #f472b6;"></i>'
ICON_CATEGORY = '<i class="fas fa-list-alt" style="color: #5a9bd4;"></i>'
ICON_QUANTITY = '<i class="fas fa-sort-numeric-up" style="color: #4caf50;"></i>'
ICON_COST = '<i class="fas fa-ruble-sign" style="color: #ff9800;"></i>'

class MpProductForm(forms.ModelForm):
    class Meta:
        model = MpProduct
        fields = ['artikul', 'category', 'kol', 'sebestoimost']
        widgets = {
            'artikul': forms.TextInput(attrs=CHILD_FRIENDLY_STYLES),
            'category': forms.Select(attrs=CHILD_FRIENDLY_STYLES),
            'kol': forms.NumberInput(attrs=CHILD_FRIENDLY_STYLES),
            'sebestoimost': forms.NumberInput(attrs=CHILD_FRIENDLY_STYLES),
        }
        labels = {
            'artikul': f"{ICON_ARTIKUL} Артикул",
            'category': f"{ICON_CATEGORY} Категория",
            'kol': f"{ICON_QUANTITY} Количество",
            'sebestoimost': f"{ICON_COST} Себестоимость",
        }


    def __init__(self, *args, **kwargs):
        super(MpProductForm, self).__init__(*args, **kwargs)
        self.fields['artikul'].label = mark_safe(f"{ICON_ARTIKUL} Артикул")
        self.fields['category'].label = mark_safe(f"{ICON_CATEGORY} Категория")
        self.fields['kol'].label = mark_safe(f"{ICON_QUANTITY} Количество")
        self.fields['sebestoimost'].label = mark_safe(f"{ICON_COST} Себестоимость")

CHILD_FRIENDLY_STYLES_Char = {
    'class': 'form-control child-friendly-input', 
    'style': 'border: 2px solid #a1daf7; border-radius: 15px; font-size: 14px; padding: 10px; margin: 10px; width: 100%;'
}

class CharacteristicForm(forms.ModelForm):
    class Meta:
        model = ProductCharacteristic
        fields = ['characteristic', 'value']
        widgets = {
            'characteristic': forms.Select(attrs=CHILD_FRIENDLY_STYLES_Char),
            'value': forms.TextInput(attrs=CHILD_FRIENDLY_STYLES_Char),
        }
        labels = {
            'characteristic': mark_safe("Характеристика"),
            'value': mark_safe("Значение"),
        }

    def __init__(self, *args, **kwargs):
        super(CharacteristicForm, self).__init__(*args, **kwargs)
        self.fields['characteristic'].label = mark_safe("Характеристика")
        self.fields['value'].label = mark_safe("Значение")

CharacteristicFormSet = formset_factory(CharacteristicForm, extra=1)