# -*- coding: utf-8 -*-
import phonenumbers
from django import template
__author__ = 'D.Ivanets'

register = template.Library()


@register.filter(name='phonenumber')
def phonenumber(value, country="US"):
    try:
        x = phonenumbers.parse(value, country)
        return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.NATIONAL)
    except phonenumbers.NumberParseException:
        return value


@register.filter(name='cardnumber')
def cardnumber(value):
    if len(value) != 16 or len(value) != 0:
        return "Incorrect"
    else:
        return value[0:4] + ' ' + value[4:8] + ' ' + value[8:12] + ' ' + value[12:16]


@register.filter(name='maskcardnumber')
def maskcardnumber(value):    
    return "*"*(len(value)-4) + value[-4:]
