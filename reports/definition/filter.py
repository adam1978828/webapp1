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


class ReportDefinitionFieldFilter():
    def __init__(self):
        self.alias = ''
        self.op_alias = ''
        self.data = ''
        self.is_final = 0

    def from_json_str(self, json_str):
        try:
            json_obj = json.loads(json_str)
        except Exception as e:
            raise ReportInvalidInputJson(str(e))

        return self.from_json_obj(json_obj)

    def from_json_obj(self, json_obj):
        self.alias = json_obj['alias']
        self.op_alias = json_obj['op_alias']
        self.data = json_obj['data']
        self.is_final = int(json_obj['is_final'])

        return self

    def to_json(self, clear_data=False):
        result = dict()

        result['alias'] = self.alias
        result['op_alias'] = self.op_alias
        result['data'] = self.data if not clear_data or self.is_final == 1 else ''
        result['is_final'] = self.is_final

        return result