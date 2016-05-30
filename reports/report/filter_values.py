#!/usr/bin/env python
"""
Contains urls for the client site authentication
"""

# imports must be placed here

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportFieldFilterValues():
    def __init__(self, key_field, value_field, values):
        self.key_field = key_field
        self.value_field = value_field
        self.values = values