#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains urls for the client site authentication
"""

from django.db.models import Avg, Min, Max, Count, Sum


__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportFieldAggregation(object):
    def __init__(self, alias, name, agg_func):
        self.alias = alias
        self.name = name
        self.agg_func = agg_func

    def build_aggregation(self, field_name, is_row_sql=False):
        if not is_row_sql:
            return self.agg_func(field_name)
        else:
            return '{0}({1}) as {2}__{3}'.format(self.alias, field_name, field_name, self.alias)


class ReportFieldAggSum(ReportFieldAggregation):
    def __init__(self, name='Sum'):
        ReportFieldAggregation.__init__(self, 'sum', name, Sum)


class ReportFieldAggAvg(ReportFieldAggregation):
    def __init__(self, name='Avg'):
        ReportFieldAggregation.__init__(self, 'avg', name, Avg)


class ReportFieldAggMin(ReportFieldAggregation):
    def __init__(self, name='Min'):
        ReportFieldAggregation.__init__(self, 'min', name, Min)


class ReportFieldAggMax(ReportFieldAggregation):
    def __init__(self, name='Max'):
        ReportFieldAggregation.__init__(self, 'max', name, Max)


class ReportFieldAggCount(ReportFieldAggregation):
    def __init__(self, name='Count'):
        ReportFieldAggregation.__init__(self, 'count', name, Count)


report_aggregations = {
    'sum': ReportFieldAggSum,
    'avg': ReportFieldAggAvg,
    'min': ReportFieldAggMin,
    'max': ReportFieldAggMax,
    'count': ReportFieldAggCount,
}