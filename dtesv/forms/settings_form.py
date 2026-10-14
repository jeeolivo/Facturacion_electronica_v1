from django import forms
from django.forms import ModelForm
from dtesv.models import Parametros, C005TipoContingencia


class SettingsForm(ModelForm):
    class Meta:
        model = Parametros
        fields = '__all__'
