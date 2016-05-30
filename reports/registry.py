#!/usr/bin/env python
"""
Contains urls for the client site authentication
"""

from django.db import connection
from django.conf import settings

from .exceptions import ReportAliasAlreadyExists, ReportAliasIsEmpty, ReportDataSourceNotExists

if getattr(settings, 'SMART_REPORT_DB_ENGINE', 'DjangoORM') == 'DjangoORM':
    from .models import *
else:
    from .SQLAlchemy_models import *

from .report.aggregation import report_aggregations
from .report.filter_operation import report_filter_operations, report_filter_ordered
from .report.field_type import report_field_types
from .report.report import Report, ReportXlsOptions
from .report.field import ReportField
from .report.filter import ReportFilter


__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI (Oleg Tegelman)"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


def dict_fetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


class ReportRegistry():
    def __init__(self):
        self.reports = dict()

    def register_report(self, val):

        if val.alias is None or val.alias.strip() == '':
            raise ReportAliasIsEmpty()

        if self.reports.get(val.alias, None) is not None:
            raise ReportAliasAlreadyExists(val.alias)

        self.reports[val.alias] = val

    def get_available_reports(self):
        result = list()

        for key in self.reports.keys():
            report = self.reports[key]
            result.append({"alias": report.alias, "name": report.readable_name})

        return result

    def get_report_by_alias(self, alias):
        if alias not in self.reports:
            return self.reload_report_from_db(alias)
        else:
            return self.reports.get(alias, None)

    def delete_report_by_alias(self, alias, reload=True):
        if alias in self.reports:
            del(self.reports[alias])

        if reload:
            report = self.reload_report_from_db(alias)
            return report
        else:
            return None

    def reload_report_from_db(self, alias):
        try:
            ds = DB_LOADERS[getattr(settings, 'SMART_REPORT_DB_ENGINE', 'DjangoORM')](alias)
            report = ds.load_report_from_db()
            self.register_report(report)
            return report
        except Exception as e:
            return None


class ReportDjangoOrmDbLoader():
    def __init__(self, source_alias):
        self.source_alias = source_alias

    def load_report_from_db(self):
        try:
            data_source = RepDataSource.objects.get(alias=self.source_alias)
        except RepDataSource.DoesNotExist:
            raise ReportDataSourceNotExists(self.source_alias)

        report_options = ReportXlsOptions(add_grouping_headers=True)
        report = Report(data_source.source, data_source.alias, data_source.name, options=report_options, source_type=data_source.source_type)

        fields = RepDataSourceField.objects.filter(data_source_id=data_source.id).order_by('order_num')

        for field in fields:
            field_filter = None
            try:
                tmp = RepDataSourceFieldFilter.objects.get(field_id=field.id)
            except RepDataSourceFieldFilter.DoesNotExist:
                tmp = None

            if tmp is not None:
                operations = RepDataSourceFieldFilterOperation.objects.filter(filter_id=tmp.id)
                tmp_list = [None] * len(report_filter_ordered)

                for op in operations:
                    tmp_list[report_filter_ordered.index(op.operation)] = report_filter_operations[op.operation]()

                filter_op_list = [x for x in tmp_list if x is not None]

                if tmp.source and tmp.source_type == 'row_sql':
                    values = list()
                    cursor = connection.cursor()
                    cursor.execute(tmp.source)
                    segment_data = dict_fetchall(cursor)

                    for val in segment_data:
                        values.append({'key': val[tmp.source_key_column], 'val': val[tmp.source_val_column]})
                else:
                    values = None

                field_filter = ReportFilter(tmp.column_name, max_count=10, operations=filter_op_list, values=values)

            aggregations = list()

            tmp = RepDataSourceFieldAggregation.objects.filter(field_id=field.id)
            for agg in tmp:
                aggregations.append(report_aggregations[agg.aggregation_type]())

            field = ReportField(field.column_name, report_field_types[field.field_type](), field.name, filters=field_filter,
                                allow_grouping=field.allow_grouping == 1, allow_ordering=field.allow_ordering, cell_width=field.column_width,
                                aggregations=aggregations, allow_display=field.allow_display == 1)
            report.add_field(field)

        return report


def get_report_builder(source_type):
    from .builder.db_view_builder import DbViewReportBuilder
    from .builder.row_sql_biulder import RowSqlReportBuilder
    from .builder.model_builder import DjangoModelReportBuilder

    if source_type == 'django_model':
        return DjangoModelReportBuilder
    elif source_type == 'view':
        return DbViewReportBuilder
    elif source_type == 'row_sql':
        return RowSqlReportBuilder
    else:
        return None


class ReportSqlAlchemyDbLoader():
    def __init__(self, source_alias):
        self.source_alias = source_alias

    def load_report_from_db(self):
        db_session = settings.SESSION()

        try:
            data_source = db_session.query(RepDataSource).filter_by(alias=self.source_alias).first()
        except Exception as e:
            raise ReportDataSourceNotExists(self.source_alias)

        report_options = ReportXlsOptions(add_grouping_headers=True)
        report = Report(data_source.source, data_source.alias, data_source.name, options=report_options, source_type=data_source.source_type)

        fields = db_session.query(RepDataSourceField).filter_by(data_source_id=data_source.id).order_by(RepDataSourceField.order_num)

        for field in fields:
            field_filter = None
            try:
                tmp = db_session.query(RepDataSourceFieldFilter).filter_by(field_id=field.id).first()
            except Exception as e:
                tmp = None

            if tmp is not None:
                operations = db_session.query(RepDataSourceFieldFilterOperation).filter_by(filter_id=tmp.id).all()
                tmp_list = [None] * len(report_filter_ordered)

                for op in operations:
                    tmp_list[report_filter_ordered.index(op.operation)] = report_filter_operations[op.operation]()

                filter_op_list = [x for x in tmp_list if x is not None]

                if tmp.source and tmp.source_type == 'row_sql':
                    values = list()
                    cursor = connection.cursor()
                    cursor.execute(tmp.source)
                    segment_data = dict_fetchall(cursor)

                    for val in segment_data:
                        values.append({'key': val[tmp.source_key_column], 'val': val[tmp.source_val_column]})
                else:
                    values = None

                field_filter = ReportFilter(tmp.column_name, max_count=10, operations=filter_op_list, values=values)

            aggregations = list()

            tmp = db_session.query(RepDataSourceFieldAggregation).filter_by(field_id=field.id).all()
            for agg in tmp:
                aggregations.append(report_aggregations[agg.aggregation_type]())

            field = ReportField(field.column_name, report_field_types[field.field_type](), field.name, filters=field_filter,
                                allow_grouping=field.allow_grouping == 1, allow_ordering=field.allow_ordering, cell_width=field.column_width,
                                aggregations=aggregations, allow_display=field.allow_display == 1, need_sub_total=field.need_sub_total == 1)
            report.add_field(field)

        return report


DB_LOADERS = {
    'DjangoORM': ReportDjangoOrmDbLoader,
    'SQLAlchemy': ReportSqlAlchemyDbLoader
}