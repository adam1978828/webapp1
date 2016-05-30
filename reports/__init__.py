#!/usr/bin/env python
"""
Contains urls for the client site authentication
"""

from .registry import ReportRegistry

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"

global report_registry
report_registry = ReportRegistry()
report_registry.reload_report_from_db('rep_deals_by_company_kiosk')
report_registry.reload_report_from_db('rep_sales_tax')