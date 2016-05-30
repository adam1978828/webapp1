# -*- coding: utf-8 -*-
from django.core.validators import ValidationError
from functools import wraps
import re, pickle
from libs.utils.string_functions import convert2camelCase, is_number, is_integer, is_float, is_gt_zero, is_enough
from libs.utils.string_functions import is_in_range_1_to_100, is_2_digits_after_point, is_gt_or_eq_zero
from libs.utils.string_functions import is_integer_limit, is_fractional_limit
from datetime import datetime

__author__ = 'D.Kalpakchi'


def json_response_content(response_type='', msg='', data=None):
    """
    Returns dictionary which reflects basic structure of json server response
    """
    return {
        'type': response_type,
        'message': msg,
        'errors': [],
        'redirect_url': '',
        'data': data or {},
        'is_need_login': True
    }


def validation_error(field, message):
    """ Returns default validation error """
    return {
        'field': field,
        'message': message
    }


def model_validator(validator):
    """
    Use this decorator for all model validators
    """
    @wraps(validator)
    def validate(object_to_validate, key, value):
        try:
            return validator(object_to_validate, key, value)
        except Exception, e:
            camelCaseKey = convert2camelCase(key)
            if not camelCaseKey in map(lambda x: x['field'], object_to_validate.errors):
                object_to_validate.errors.append(validation_error(camelCaseKey, unicode(e.message)))

    return validate


def validate_length_of(value, min_value=0, max_value=float('inf')):
    """
    Validate length of value field in range from min to max
    """
    if not min_value <= len(value) <= max_value:
        if max_value == float('inf'):
            raise ValidationError('Length must be greater than %.1f' % min_value)
        elif min_value == float('inf'):
            raise ValidationError('Length must be less than %.1f' % max_value)
        elif min_value == max_value:
            raise ValidationError('Length must be equal %.1f' % max_value)
        else:
            raise ValidationError(
                "Length must be in range from %.1f to %.1f" % (min_value, max_value))


def validate_type_of(value, expected_type):
    """
    Validates if value is of expected type
    Requirement:
        expected_type must be one of the types contained in built-in python types module
    Examples:
        from types import *
        from libs.validators.core import validate_type_of

        validate_type_of('dsgfgdfsgdfgd', StringType) # returns None
        validate_type_of('sdgsdgsd', BooleanType)     # returns ValidationError
    """
    if not type(value) == expected_type:
        raise ValidationError(
            'Expect the value to be %s, received %s' % (expected_type, type(value)))


def validate_format_of(value, expected_format, message='Wrong format'):
    """ Validates format of value with format regular expression """
    if not re.match(expected_format, value):
        raise ValidationError(message)


def validate_range_of(value, min_value=-float('inf'), max_value=float('inf')):
    if not min_value <= value <= max_value:
        raise ValidationError(
            "Value of this field must be in range from %.1f to %.1f" % (min_value, max_value))


def validate_numericality_of(value):
    if not is_number(value):
        raise ValidationError("This field must be a number")


def validate_less_than(small_value, big_value):
    if small_value > big_value:
        raise ValidationError("This field must be less than or equal \'# of times to be used\' field")


def validate_float_0_to_1(count_param, value):
    if not is_float(value):
        raise ValidationError(count_param + " field must be a float")
    if not 0 < float(value) < 1:
        raise ValidationError(count_param + " field must be in the interval from 0 to 100")

def validate_integer_gt_zero(count_param, value):
    if not is_integer(value):
        raise ValidationError(count_param + " field must be a integer")
    if not is_gt_zero(value):
        raise ValidationError(count_param + " field must be greater than zero")


def validate_float_gt_zero(count_param, value):
    if not is_float(value):
        raise ValidationError(count_param + " field must be a float or integer")
    if not is_gt_zero(value):
        raise ValidationError(count_param + " field must be greater than zero")
    if not is_enough(value):
        raise ValidationError(count_param + " field must be more or equal 0.01")
    if not is_2_digits_after_point(value):
        raise ValidationError(count_param + " field must be two digits after the decimal point")


def validate_integer_1_to_100(count_param, value):
    if not is_integer(value):
        raise ValidationError(count_param + " field must be a integer")
    if not is_in_range_1_to_100(value):
        raise ValidationError(count_param + " field must be in the interval from 1 to 100")


def validate_float_gt_or_eq_zero(value):
    if not is_float(value):
        raise ValidationError("This field must be a float")
    if not is_gt_or_eq_zero(value):
        raise ValidationError("This field must be equal or greater than zero")

def validate_numeric(value, integer, fractional):
    if not is_float(value):
        raise ValidationError("This field must be a float")
    if not is_integer_limit(value, integer):
        raise ValidationError("Integer part must be no more than "+str(integer)+" digits")
    if not is_fractional_limit(value, fractional):
        raise ValidationError("Fractional part must be no more than "+str(fractional)+" digits")

def validate_card_expiry(value):
    if not len(value):
        raise ValidationError("Empty field")
    if not ('/' in value):
        raise ValidationError('Field must be with the mask MM/YY')
    card_expiry_month, card_expiry_year = value.split('/')
    if not card_expiry_month:
        raise ValidationError("Empty field month")
    elif not re.match("^[0-9]*$", card_expiry_month):
        raise ValidationError("Month need only digits")
    elif not (int(card_expiry_month) in range(1, 13)):
        raise ValidationError("Month In the interval from 1 to 12")
    if not card_expiry_year:
        raise ValidationError("Empty field year")
    elif not re.match("^[0-9]*$", card_expiry_year):
        raise ValidationError("Year need only digits")
    elif not (len(card_expiry_year) <= 2):
        raise ValidationError("Year need only 2 digits")
    now = int(datetime.utcnow().strftime('%y%m'))
    int_year, int_month = int(card_expiry_year), int(card_expiry_month)
    set = int('{0:02d}{1:02d}'.format(int_year, int_month))
    if not set >= now:
        raise ValidationError("The card has expired maintenance")
    return '{0:02d}{1:02d}'.format(int_month, int_year)