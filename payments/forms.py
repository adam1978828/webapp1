from django import forms
from django.core.validators import RegexValidator

__author__ = 'Denis Ivanets (denself@gmail.com)'


err_message = "Gateway ID should be like AB1234-56"
gateway_validator = RegexValidator(regex=r'^[A-Z]{1,2}\d{4,5}\-\d{2}$',
                                   message=err_message)


class FirstDataForm(forms.Form):
    ps_id = forms.IntegerField(min_value=1, max_value=2)
    gateway_id = forms.CharField(validators=[gateway_validator],
                                 min_length=1, max_length=10, required=True)
    password = forms.CharField(min_length=8, max_length=32, required=True)
    key_id = forms.CharField(min_length=5, max_length=8, required=True)
    hmac_key = forms.CharField(min_length=1, max_length=32, required=True)
