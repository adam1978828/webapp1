#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains urls for the client site authentication
"""

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportFieldOrder(object):
    def __init__(self, alias, name, prefix):
        self.alias = alias
        self.name = name
        self.prefix = prefix

    def build_order_by_field(self, field_name, is_row_sql=False):
        if not is_row_sql:
            return '{0}{1}'.format(self.prefix, field_name)
        else:
            return '{0} {1}'.format(field_name, self.alias)


class ReportFieldOrderAsc(ReportFieldOrder):
    def __init__(self, name='Ascending'):
        ReportFieldOrder.__init__(self, 'asc', name, '')


class ReportFieldOrderDesc(ReportFieldOrder):
    def __init__(self, name='Descending'):
        ReportFieldOrder.__init__(self, 'desc', name, '-')