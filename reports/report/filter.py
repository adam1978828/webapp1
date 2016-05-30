#!/usr/bin/env python
"""
Contains urls for the client site authentication
"""

import json

from .filter_operation import ReportFieldFilterOperation
from ..exceptions import ReportInvalidSubClassException, ReportInvalidInputJson


__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportFilter(object):
    def __init__(self, search_field, max_count=1, operations=None, values=None):
        self.search_field = search_field
        self.max_count = max_count
        self.operations = operations if operations else list()
        self.values = values

        self.__validate_operations()

    def add_operation(self, val):
        if not issubclass(type(val), ReportFieldFilterOperation):
            raise ReportInvalidSubClassException(type(val).__name__, ReportFieldFilterOperation.__name__)
        self.operations.append(val)

    def get_filter_operation(self, alias):
        result = None

        for obj in self.operations:
            if obj.alias == alias:
                result = obj
                break

        return result

    def build_filter(self, data, op_alias, is_row_sql=False):
        result = None
        op = self.get_filter_operation(op_alias)

        if op is not None:
            result = op.get_filter(self.search_field, data, is_row_sql)

        return result

    def __validate_operations(self):
        for val in self.operations:
            if not issubclass(type(val), ReportFieldFilterOperation):
                raise ReportInvalidSubClassException(type(val).__name__, ReportFieldFilterOperation.__name__)