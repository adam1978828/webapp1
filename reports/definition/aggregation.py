#!/usr/bin/env python
"""
Contains urls for the client site authentication
"""

from django.db.models import Avg, Min, Max, Count, Sum
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


class ReportDefinitionFieldAggregation():
    def __init__(self):
        self.alias = ''
        self.agg_alias = ''
        self.header = ''

    def from_json_str(self, json_str):
        try:
            json_obj = json.loads(json_str)
        except Exception as e:
            raise ReportInvalidInputJson(str(e))

        return self.from_json_obj(json_obj)

    def from_json_obj(self, json_obj):
        self.alias = json_obj['alias']
        self.agg_alias = json_obj['agg_alias']
        self.header = json_obj['header']

        return self

    def to_json(self):
        result = dict()

        result['alias'] = self.alias
        result['agg_alias'] = self.agg_alias
        result['header'] = self.header

        return result