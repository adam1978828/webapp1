#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains urls for the client site authentication
"""

import datetime

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportFieldType(object):
    def __init__(self, alias, name, value_format):
        self.alias = alias
        self.name = name
        self.value_format = value_format

    def from_str(self, value):
        pass

    def to_str(self, value):
        pass


class ReportFieldTypeString(ReportFieldType):
    def __init__(self, name='String', value_format=None):
        ReportFieldType.__init__(self, 'string', name, value_format if value_format else '{0}')

    def from_str(self, value):
        return value

    def to_str(self, value):
        if value is None or value == '':
            return ''
        return self.value_format.format(value)


class ReportFieldTypeInteger(ReportFieldType):
    def __init__(self, name='Integer', value_format=None):
        ReportFieldType.__init__(self, 'integer', name, value_format if value_format else '{0}')

    def from_str(self, value):
        if value is None or value == '':
            return None
        return int(value)

    def to_str(self, value):
        if value is None or value == '':
            return ''
        return self.value_format.format(value)


class ReportFieldTypeFloat(ReportFieldType):
    def __init__(self, name='Float', value_format=None):
        ReportFieldType.__init__(self, 'float', name, value_format if value_format else '{:.2f}')

    def from_str(self, value):
        if value is None or value == '':
            return None
        return float(value.replace(",", "."))

    def to_str(self, value):
        if value is None or value == '':
            return ''
        return self.value_format.format(value)


class ReportFieldTypeDateTime(ReportFieldType):
    def __init__(self, name='Datetime', value_format=None):
        ReportFieldType.__init__(self, 'datetime', name, value_format if value_format else '%m/%d/%y %H:%M')

    def from_str(self, value):
        if value is None or value == '':
            return None
        return datetime.datetime.strptime(value, self.value_format)

    def to_str(self, value):
        if value is None or value == '':
            return ''
        return value.strftime(self.value_format)


class ReportFieldTypeDate(ReportFieldType):
    def __init__(self, name='Date', value_format=None):
        ReportFieldType.__init__(self, 'date', name, value_format if value_format else '%m/%d/%y')

    def from_str(self, value):
        if value is None or value == '':
            return None
        return datetime.datetime.strptime(value, self.value_format).date()

    def to_str(self, value):
        if value is None or value == '':
            return ''
        return value.strftime(self.value_format)


report_field_types = {
    'string': ReportFieldTypeString,
    'integer': ReportFieldTypeInteger,
    'float': ReportFieldTypeFloat,
    'datetime': ReportFieldTypeDateTime,
    'date': ReportFieldTypeDate,
}