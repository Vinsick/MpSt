from django import forms
from .models import OzonSettings

class OzonSettingsForm(forms.ModelForm):
    class Meta:
        model = OzonSettings
        fields = ['client_id', 'client_key', 'name']
        widgets = {
            'client_id': forms.TextInput(attrs={'class': 'form-control'}),
            'client_key': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название',
            'client_id': 'ID',
            'client_key': 'Api-Key'
        }