#!/usr/bin/env python
"""
Contains urls for the client site authentication
"""

from .field_order import *
from .aggregation import ReportFieldAggregation
from .filter import ReportFilter
from ..exceptions import ReportInvalidSubClassException


__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportField(object):
    def __init__(self, model_field_name, field_type, readable_name=None, filters=None, aggregations=None,
                 allow_ordering=False, allow_grouping=False, allow_display=True, cell_width=None, need_sub_total=None):
        self.model_field_name = model_field_name
        self.readable_name = readable_name if readable_name else model_field_name
        self.filters = filters
        self.aggregations = aggregations if aggregations else list()
        self.allow_ordering = allow_ordering
        self.allow_grouping = allow_grouping
        self.allow_display = allow_display
        self.need_sub_total = need_sub_total
        self.field_type = field_type
        self.orders = None
        self.cell_width = cell_width

        if allow_ordering:
            self.orders = [ReportFieldOrderAsc(), ReportFieldOrderDesc()]

        self.__validate_aggregations()
        self.__validate_filters()

    def add_aggregation(self, val):
        if not issubclass(type(val), ReportFieldAggregation):
            raise ReportInvalidSubClassException(type(val).__name__, ReportFieldAggregation.__name__)

        self.aggregations.append(val)

    def get_aggregation(self, agg_alias):
        result = None

        for val in self.aggregations:
            if val.alias == agg_alias:
                result = val
                break
        return result

    def get_order_by(self, order_by_alias):
        result = None

        for val in self.orders:
            if val.alias == order_by_alias:
                result = val
                break

        return result

    def __validate_filters(self):
        if self.filters is not None and not issubclass(type(self.filters), ReportFilter):
            raise ReportInvalidSubClassException(type(self.filters).__name__, ReportFilter.__name__)

    def __validate_aggregations(self):
        for tmp in self.aggregations:
            if not issubclass(type(tmp), ReportFieldAggregation):
                raise ReportInvalidSubClassException(type(tmp).__name__, ReportFieldAggregation.__name__)