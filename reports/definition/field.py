#!/usr/bin/env python
"""
Contains urls for the client site authentication
"""

from ..exceptions import ReportInvalidInputJson
import json


__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportDefinitionField():
    def __init__(self):
        self.alias = ''
        self.header = ''
        self.sub_fields = list()
        self.row_span = 1
        self.col_span = 1
        self.cell_width = None

    def from_json_str(self, json_str):
        try:
            json_obj = json.loads(json_str)
        except Exception as e:
            raise ReportInvalidInputJson(str(e))

        return self.from_json_obj(json_obj)

    def from_json_obj(self, json_obj):
        self.alias = json_obj['alias']
        self.header = json_obj['header']

        if 'row_span' in json_obj:
            self.row_span = json_obj['row_span']

        if 'col_span' in json_obj:
            self.row_span = json_obj['col_span']

        for obj in json_obj['sub_fields']:
            tmp_field = ReportDefinitionField()
            tmp_field = tmp_field.from_json_obj(obj)
            self.sub_fields.append(tmp_field)

        return self

    def to_json(self):
        result = dict()
        result['alias'] = self.alias
        result['header'] = self.header
        result['row_span'] = self.row_span
        result['col_span'] = self.col_span
        result['sub_fields'] = list()

        for sub_field in self.sub_fields:
            result['sub_fields'].append(sub_field.to_json())

        return result