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


class ReportException(Exception):
    def __init__(self, message):
        self.message = message

    def __unicode__(self):
        return self.message


class ReportInvalidClassException(ReportException):
    def __init__(self, actual_class, expected_class):
        self.message = 'Variable type is <<{0}>> but expected <<{1}>>'
        self.actual_class = actual_class
        self.expected_class = expected_class

    def __unicode__(self):
        return self.message.format(self.actual_class, self.expected_class)


class ReportInvalidSubClassException(ReportException):
    def __init__(self, actual_class, expected_class):
        self.message = 'Variable class type is <<{0}>> but expected subclass type <<{1}>>'
        self.actual_class = actual_class
        self.expected_class = expected_class

    def __unicode__(self):
        return self.message.format(self.actual_class, self.expected_class)


class ReportAliasAlreadyExists(ReportException):
    def __init__(self, alias):
        self.message = 'Report with alias <<{0}>> already exists'
        self.alias = alias

    def __unicode__(self):
        return self.message.format(self.alias)


class ReportAliasIsEmpty(ReportException):
    def __init__(self):
        self.message = 'Report alias can''t be empty'

    def __unicode__(self):
        return self.message


class ReportInvalidInputJson(ReportException):
    def __init__(self, custom_message):
        self.custom_message = custom_message
        self.message = 'Report json is invalid! Error: {0}'

    def __unicode__(self):
        return self.message.format(self.custom_message)


class ReportDataSourceNotExists(ReportException):
    def __init__(self, source_alias):
        self.source_alias = source_alias
        self.message = 'Data source with alias <<{0}>> does not exist in database'

    def __unicode__(self):
        return self.message.format(self.source_alias)