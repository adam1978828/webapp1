#!/usr/bin/env python
"""

"""

from django.db import models

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, Vyruchayka"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class RepDataSource(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    alias = models.CharField(unique=True, max_length=100)
    source = models.TextField(blank=True)
    source_type = models.CharField(max_length=20, blank=True)

    class Meta:
        managed = False
        db_table = 'rep_data_source'


class RepDataSourceField(models.Model):
    id = models.AutoField(primary_key=True)
    column_name = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    column_width = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    allow_ordering = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True)
    allow_grouping = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True)
    allow_display = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True)
    field_type = models.CharField(max_length=20, blank=True)
    data_source = models.ForeignKey(RepDataSource)
    order_num = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'rep_data_source_field'


class RepDataSourceFieldAggregation(models.Model):
    id = models.AutoField(primary_key=True)
    field = models.ForeignKey(RepDataSourceField)
    aggregation_type = models.CharField(max_length=20, blank=True)

    class Meta:
        managed = False
        db_table = 'rep_data_source_field_aggregation'


class RepDataSourceFieldFilter(models.Model):
    id = models.AutoField(primary_key=True)
    field = models.ForeignKey(RepDataSourceField)
    column_name = models.CharField(max_length=200)
    source = models.TextField(blank=True)
    source_key_column = models.CharField(max_length=200, blank=True)
    source_val_column = models.CharField(max_length=200, blank=True)
    source_type = models.CharField(max_length=20, blank=True)

    class Meta:
        managed = False
        db_table = 'rep_data_source_field_filter'


class RepDataSourceFieldFilterOperation(models.Model):
    id = models.AutoField(primary_key=True)
    filter = models.ForeignKey(RepDataSourceFieldFilter)
    operation = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = False
        db_table = 'rep_data_source_field_filter_operation'