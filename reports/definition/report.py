#!/usr/bin/env python
"""

"""

from .aggregation import ReportDefinitionFieldAggregation
from .field_order import ReportDefinitionFieldOrder
from .filter import ReportDefinitionFieldFilter
from .field import ReportDefinitionField
from ..exceptions import ReportInvalidInputJson

import json

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, Vyruchayka"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportDefinition():
    def __init__(self):
        self.alias = ''
        self.header = ''
        self.sub_header = ''
        self.fields = list()
        self.filters = list()
        self.filter_operation = ''
        self.aggregations = list()
        self.group_by_fields = list()
        self.order_by_fields = list()

    def from_json(self, json_str):
        try:
            json_obj = json.loads(json_str)
        except Exception as e:
            raise ReportInvalidInputJson(str(e))

        self.alias = json_obj['alias']
        self.header = json_obj['header']
        #self.sub_header = json_obj['sub_header']
        self.filter_operation = json_obj['filter_operation']

        for obj in json_obj['fields']:
            tmp_field = ReportDefinitionField()
            tmp_field = tmp_field.from_json_obj(obj)
            self.fields.append(tmp_field)

        for obj in json_obj['filters']:
            tmp_filter = ReportDefinitionFieldFilter()
            tmp_filter.from_json_obj(obj)
            self.filters.append(tmp_filter)

        for obj in json_obj['order_by_fields']:
            tmp_order = ReportDefinitionFieldOrder()
            tmp_order = tmp_order.from_json_obj(obj)
            self.order_by_fields.append(tmp_order)

        for obj in json_obj['aggregations']:
            tmp_agg = ReportDefinitionFieldAggregation()
            tmp_agg = tmp_agg.from_json_obj(obj)
            self.aggregations.append(tmp_agg)

        for obj in json_obj['group_by_fields']:
            self.group_by_fields.append(obj)

    def to_json(self, clear_filter_data=False):
        result = dict()

        result['alias'] = self.alias
        result['header'] = self.header
        result['sub_header'] = self.sub_header
        result['filter_operation'] = self.filter_operation

        result['fields'] = list()
        for val in self.fields:
            result['fields'].append(val.to_json())

        result['filters'] = list()
        for val in self.filters:
            result['filters'].append(val.to_json(clear_filter_data))

        result['aggregations'] = list()
        for val in self.aggregations:
            result['aggregations'].append(val.to_json())

        result['group_by_fields'] = list()
        for val in self.group_by_fields:
            result['group_by_fields'].append(val)

        result['order_by_fields'] = list()
        for val in self.order_by_fields:
            result['order_by_fields'].append(val.to_json())

        return json.dumps(result)

    def validate_report(self, is_report):
        result = []
        if self.header == '':
            result.append('Name for the {0} must be specified!'.format('report' if is_report else 'template'))

        if not self.fields:
            result.append('Fields for data output must be specified!')

        #is_valid_grouping = True
        #if self.group_by_fields:
        #    for order_by in self.order_by_fields:
        #        if order_by.alias not in self.group_by_fields:
        #            is_valid_grouping = False
        #            break

        #if not is_valid_grouping:
        #    result.append('Not all order by fields included to the group by!')

        return result