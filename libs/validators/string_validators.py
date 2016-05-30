import re

from django.core.validators import ValidationError, URLValidator

from libs.utils.string_functions import is_number


__author__ = 'D.Kalpakchi'


url_validator = URLValidator()


def validate_string_not_empty(value):
    if value in [u'', None]:
        raise ValidationError("This value is required")


def validate_is_not_numeric(value):
    if is_number(value):
        raise ValidationError("This value can not be number")

def validate_zip_code_string(value):
    if len(value) != 5:
        raise ValidationError("This value length is not 5 characters")
    if not value.isdigit():
        raise ValidationError("This value consists not only of numbers")


def validate_string_hex(value):
    if not re.match(re.compile('^([0-9ABCDEF])+$'), value):
        raise ValidationError('Wrong format. Only 0-9 and A-F are permitted.')


def validate_url(value):
    url_validator('http://'+value)


if __name__ == '__main__':
    print validate_url('google.com')
    print validate_url('google.com:8080')
    print validate_url('127.0.0.1')
    print validate_url('127.0.0.1:8080')
    print validate_url('localhost')
    print validate_url('http://google.com')