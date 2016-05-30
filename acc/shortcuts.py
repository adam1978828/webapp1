# -*- coding: utf-8 -*-
import phonenumbers as pn
from Model import Address
from django.core.validators import ValidationError

__author__ = 'D.Ivanets'


def address_from_request(post, address=None):
    if not address:
        address = Address()
    address.line_1 = post.get('line_1', '')
    address.line_2 = post.get('line_2', '')
    address.latitude = post.get('latitude', '')
    address.longitude = post.get('longitude', '')
    address.city = post.get('i_city', '')
    address.state = post.get('i_state', '')
    address.postalcode = post.get('i_post', '')
    address.country = post.get('i_country', '')
    return address

def address_from_request_for_profile(post, address=None):
    if not address:
        address = Address()
    address.line_2 = post.get('line_2', '')
    address.city = post.get('i_city', '')
    address.state = post.get('i_state', '')
    address.postalcode = post.get('i_post', '')
    address.country = post.get('i_country', '')
    return address

def phone_number_from_request(post, field_name='i_phone', country_code="US"):
    phone = post.get(field_name, '')
    if not phone:
        return ''
    elif len(phone) < 7:
        raise ValidationError('Phone number is not valid')
    else:
        try:
            phone = pn.format_number(pn.parse(phone, country_code),
                                     pn.PhoneNumberFormat.E164)
        except:
            raise ValidationError('Phone number is not valid')
    return phone
