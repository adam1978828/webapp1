#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains urls for the client site authentication
"""

from django.db.models import Q


__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportFieldFilterOperation(object):
    operators = {
        'exact': '= %s',
        'not_exact': '<> %s',
        'iexact': '= UPPER(%s)',
        'not_iexact': '<> UPPER(%s)',
        'contains': 'LIKE %s%',
        'not_contains': 'NOT LIKE %s',
        'icontains': 'LIKE UPPER(%s)',
        'not_icontains': 'NOT LIKE UPPER(%s)',
        'regex': '~ %s',
        'iregex': '~* %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s',
        'not_startswith': 'LIKE %s',
        'endswith': 'LIKE %s',
        'not_endswith': 'NOT LIKE %s',
        'istartswith': 'LIKE UPPER(%s)',
        'not_istartswith': 'NOT LIKE UPPER(%s)',
        'iendswith': 'LIKE UPPER(%s)',
        'not_iendswith': 'NOT LIKE UPPER(%s)',
    }

    operation_field_wrapper = {
        'iexact': 'UPPER',
        'not_iexact': 'UPPER',
        'icontains': 'UPPER',
        'not_icontains': 'UPPER',
        'istartswith': 'UPPER',
        'not_istartswith': 'UPPER',
        'iendswith': 'UPPER',
        'not_iendswith': 'UPPER',
    }

    operation_field_value_pref_suf = {
        'contains': {'prefix': '%', 'suffix': '%'},
        'not_contains': {'prefix': '%', 'suffix': '%'},
        'icontains': {'prefix': '%', 'suffix': '%'},
        'not_icontains': {'prefix': '%', 'suffix': '%'},
        'startswith': {'prefix': '', 'suffix': '%'},
        'not_startswith': {'prefix': '', 'suffix': '%'},
        'endswith': {'prefix': '%', 'suffix': ''},
        'not_endswith': {'prefix': '%', 'suffix': ''},
        'istartswith': {'prefix': '', 'suffix': '%'},
        'not_istartswith': {'prefix': '', 'suffix': '%'},
        'iendswith': {'prefix': '%', 'suffix': ''},
        'not_iendswith': {'prefix': '%', 'suffix': ''},
    }

    def __init__(self, alias, name, orm_suffix, is_not):
        self.alias = alias
        self.name = name
        self.orm_suffix = orm_suffix
        self.is_not = is_not
        self.sql_alias = ('not_' if is_not else '') + orm_suffix.replace('__', '')

    def get_filter(self, field_name, field_data=None, is_row_sql=False):

        if not is_row_sql:
            return self.__get_orm_filter(field_name, field_data)
        else:
            return self.__get_row_sql_filter(field_name), self.operation_field_value_pref_suf.get(self.sql_alias, None)

    def __get_orm_filter(self, field_name, field_data):
        search_data = {field_name+self.orm_suffix: field_data}

        return ~Q(**search_data) if self.is_not else Q(**search_data)

    def __get_row_sql_filter(self, field_name):
        wrapper = self.operation_field_wrapper.get(self.sql_alias, None)
        if wrapper:
            field_name = '{0}({1})'.format(wrapper, field_name)
        return '{0} {1}'.format(field_name, self.operators[self.sql_alias])


class ReportFieldFilterOpEqual(ReportFieldFilterOperation):
    def __init__(self, name='Equal'):
        ReportFieldFilterOperation.__init__(self, 'equal', name, '__exact', False)


class ReportFieldFilterOpNotEqual(ReportFieldFilterOperation):
    def __init__(self, name='Not equal'):
        ReportFieldFilterOperation.__init__(self, 'not_equal', name, '__exact', True)


class ReportFieldFilterOpStartWith(ReportFieldFilterOperation):
    def __init__(self, name='Start with'):
        ReportFieldFilterOperation.__init__(self, 'start_with', name, '__istartswith', False)


class ReportFieldFilterOpNotStartWith(ReportFieldFilterOperation):
    def __init__(self, name='Not start with'):
        ReportFieldFilterOperation.__init__(self, 'not_start_with', name, '__istartswith', True)


class ReportFieldFilterOpEndWith(ReportFieldFilterOperation):
    def __init__(self, name='Ends with'):
        ReportFieldFilterOperation.__init__(self, 'end_with', name, '__iendswith', False)


class ReportFieldFilterOpNotEndWith(ReportFieldFilterOperation):
    def __init__(self, name='Not ends with'):
        ReportFieldFilterOperation.__init__(self, 'not_end_with', name, '__iendswith', True)


class ReportFieldFilterOpContain(ReportFieldFilterOperation):
    def __init__(self, name='Contains'):
        ReportFieldFilterOperation.__init__(self, 'contains', name, '__icontains', False)


class ReportFieldFilterOpNotContain(ReportFieldFilterOperation):
    def __init__(self, name='Not contains'):
        ReportFieldFilterOperation.__init__(self, 'not_contains', name, '__icontains', True)


class ReportFieldFilterOpGreater(ReportFieldFilterOperation):
    def __init__(self, name='Greater'):
        ReportFieldFilterOperation.__init__(self, 'greater', name, '__gt', False)


class ReportFieldFilterOpGreaterOrEqual(ReportFieldFilterOperation):
    def __init__(self, name='Greater or equal'):
        ReportFieldFilterOperation.__init__(self, 'greater_or_equal', name, '__gte', False)


class ReportFieldFilterOpLess(ReportFieldFilterOperation):
    def __init__(self, name='Less'):
        ReportFieldFilterOperation.__init__(self, 'less', name, '__lt', False)


class ReportFieldFilterOpLessOrEqual(ReportFieldFilterOperation):
    def __init__(self, name='Less or equal'):
        ReportFieldFilterOperation.__init__(self, 'less_or_equal', name, '__lte', False)


report_filter_operations = {
    'equal': ReportFieldFilterOpEqual,
    'not_equal': ReportFieldFilterOpNotEqual,
    'start_with': ReportFieldFilterOpStartWith,
    'not_start_with': ReportFieldFilterOpNotStartWith,
    'end_with': ReportFieldFilterOpEndWith,
    'not_end_with': ReportFieldFilterOpNotEndWith,
    'contains': ReportFieldFilterOpContain,
    'not_contains': ReportFieldFilterOpNotContain,
    'greater': ReportFieldFilterOpGreater,
    'greater_or_equal': ReportFieldFilterOpGreaterOrEqual,
    'less': ReportFieldFilterOpLess,
    'less_or_equal': ReportFieldFilterOpLessOrEqual
}

report_filter_ordered = ['contains',
                         'not_contains',
                         'start_with',
                         'not_start_with',
                         'end_with',
                         'not_end_with',
                         'equal',
                         'not_equal',
                         'greater',
                         'greater_or_equal',
                         'less',
                         'less_or_equal'
]