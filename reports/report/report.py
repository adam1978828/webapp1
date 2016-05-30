#!/usr/bin/env python
"""
Contains urls for the client site authentication
"""

from django.db.models.base import ModelBase

from ..exceptions import ReportInvalidClassException
from .field import ReportField
from ..writer.xls import ReportXlsOptions


__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class Report(object):
    def __init__(self, model, alias, readable_name, fields=None, options=ReportXlsOptions(), source_type='django_model'):
        self.source_type = source_type
        self.model = model
        self.alias = alias
        self.readable_name = readable_name
        self.fields = fields if fields else list()
        self.field_dict = dict()
        self.options = options

        self.__validate_fields()
        self.__validate_options()

        if source_type == 'django_model':
            self.__validate_model()

        self.__fields_list_to_dict()

    def __fields_list_to_dict(self):
        for field in self.fields:
            self.field_dict[field.model_field_name] = field

    def add_field(self, field):
        if not issubclass(type(field), ReportField):
            raise ReportInvalidClassException(type(field).__name__, ReportField.__name__)
        self.fields.append(field)
        self.field_dict[field.model_field_name] = field

    def __validate_fields(self):
        for field in self.fields:
            if not issubclass(type(field), ReportField):
                raise ReportInvalidClassException(type(field).__name__, ReportField.__name__)

    def __validate_options(self):
        if not issubclass(type(self.options), ReportXlsOptions):
            raise ReportInvalidClassException(type(self.options).__name__, ReportField.__name__)

    def __validate_model(self):
        if not issubclass(type(self.model), ModelBase):
            raise ReportInvalidClassException(type(self.model).__name__, ModelBase.__name__)

    def get_field_by_alias(self, field_alias):
        return self.field_dict.get(field_alias, None)

    def get_field_type_by_alias(self, field_alias):
        result = None
        field = self.field_dict.get(field_alias, None)

        if field:
            result = field.field_type

        return result

    def get_report_for_template(self):

        self.__validate_fields()
        self.__validate_options()

        if self.source_type == 'django_model':
            self.__validate_model()

        filters = list()
        aggregations = list()
        orders = list()
        grouping = list()
        fields = list()
        dt_columns = list()

        result = dict()

        for field in self.fields:
            if field.filters:
                filters.append(field.__dict__)

            if field.orders:
                orders.append(field.__dict__)

            if field.aggregations:
                aggregations.append(field.__dict__)

            if field.allow_grouping:
                grouping.append(field)

            if field.allow_display:
                fields.append(field)
                dt_columns.append({"data": field.model_field_name})

        result['filters'] = filters
        result['orders'] = orders
        result['aggregations'] = aggregations
        result['grouping'] = grouping
        result['fields'] = fields
        result['options'] = self.options
        result['alias'] = self.alias
        result['readable_name'] = self.readable_name
        result['dt_columns'] = dt_columns

        return result