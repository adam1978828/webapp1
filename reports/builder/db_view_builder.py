#!/usr/bin/env python
"""

"""

from django.db import connection
from .base import ReportBuilder
from ..report.aggregation import ReportFieldAggSum

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, Vyruchayka"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class DbViewReportBuilder(ReportBuilder):
    def build_filters(self):
        filters = list()
        data = list()

        filter_operation = ' {0} '.format(self.report_definition.filter_operation)

        for val in self.report_definition.filters:
            field = self.report.get_field_by_alias(val.alias)

            if field is not None and field.filters is not None:
                tmp_data = field.field_type.from_str(val.data)
                tmp_filter = field.filters.build_filter(None, val.op_alias, True)

                if tmp_filter is not None:
                    res_filter = tmp_filter[0]
                    res_pref_suf = tmp_filter[1]
                    filters.append(res_filter)

                    if res_pref_suf:
                        data.append(res_pref_suf['prefix'] + tmp_data + res_pref_suf['suffix'])
                    else:
                        data.append(tmp_data)

        filter_str = filter_operation.join(filters)
        if self.custom_where_clause is not None:
            filter_str = '{0} = %s {1}'.format(self.custom_where_clause[0],  'and ({0})'.format(filter_str) if filter_str else '')
            data = [self.custom_where_clause[1]] + data

        return {'filter': filter_str, 'params': data}

    def build_aggregations(self):
        aggregations = list()

        for val in self.report_definition.aggregations:
            field = self.report.get_field_by_alias(val.alias)

            if field is not None and field.aggregations is not None:
                agg_op = field.get_aggregation(val.agg_alias)
                aggregations.append({'op': agg_op.build_aggregation(field.model_field_name, True),
                                     'res_field': '{0}__{1}'.format(field.model_field_name, val.agg_alias),
                                     'alias': field.model_field_name,
                                     'header': val.header})

        return aggregations

    def build_order_by(self):
        order_by_fields = list()

        for val in self.report_definition.order_by_fields:
            field = self.report.get_field_by_alias(val.alias)

            if field is not None and field.allow_ordering:
                order_by = field.get_order_by(val.order)
                order_by_fields.append(order_by.build_order_by_field(field.model_field_name, is_row_sql=True))

        return ', '.join(order_by_fields)

    def build_sub_total(self, sub_total_fields):
        sub_totals = list()
        agg_op = ReportFieldAggSum()

        for val in sub_total_fields:
            sub_totals.append({'op': agg_op.build_aggregation(val, True),
                               'res_field': '{0}__{1}'.format(val, agg_op.alias),
                               'alias': val})
        return sub_totals

    def build_row_sql(self, filters, order_by, limit, offset, columns='*', group_by=None):
        pattern = 'select {0} from {1}'.format(columns, self.report.model)

        if filters['filter'] != '':
            pattern = pattern + ' where ' + filters['filter']

        if order_by != '':
            pattern = pattern + ' order by ' + order_by

        if group_by:
            pattern = pattern + ' group by ' + group_by

        if limit:
            pattern = pattern + ' limit ' + str(limit)

        if offset:
            pattern = pattern + ' offset ' + str(offset)

        return pattern

    def extract_data(self, filters, order_by, limit, offset):
        cursor = connection.cursor()

        cursor.execute(self.build_row_sql(filters, order_by, limit, offset), filters['params'])
        rep_data_tmp = dict_fetchall(cursor)

        return rep_data_tmp

    def extract_data_count(self, filters, order_by, limit, offset):
        row_sql = 'select count(tmp.*) as rec_count from ({0}) tmp'.format(self.build_row_sql(filters, order_by, limit, offset))
        cursor = connection.cursor()
        cursor.execute(row_sql, filters['params'])
        rep_data_tmp = dict_fetchall(cursor)

        return rep_data_tmp[0]

    def build_report_data(self, aggregations, filters, order_by, group_by, data_fields, limit=None, offset=None, sub_totals=None):

        cursor = connection.cursor()
        result = list()
        agg_data = list()

        #TODO: refactor aggregations -> select only one time
        for val in aggregations:
            cursor.execute(self.build_row_sql(filters, '', limit, offset, columns=val['op']), filters['params'])
            agg_data_tmp = dict_fetchall(cursor)

            field_type = self.report.get_field_type_by_alias(val['alias'])
            tmp_val = field_type.to_str(agg_data_tmp[0][val['res_field']])

            agg_data.append({'header': val['header'], 'data': tmp_val})

        rep_data_tmp = self.extract_data(filters, order_by, limit, offset)

        if not group_by:
            sub_total_data = list()
            if sub_totals:
                tmp_dict = dict()
                for val in sub_totals:
                    cursor.execute(self.build_row_sql(filters, '', limit, offset, columns=val['op']), filters['params'])
                    data_tmp = dict_fetchall(cursor)

                    field_type = self.report.get_field_type_by_alias(val['alias'])
                    tmp_dict[val['alias']] = field_type.to_str(data_tmp[0][val['res_field']])

                for val in data_fields:
                    sub_total_data.append(tmp_dict[val] if val in tmp_dict else '')

            result.append({'agg_caption': None, 'agg_data': agg_data,
                           'rep_data': self.rep_data_to_list(rep_data_tmp, data_fields),
                           'sub_total_data': sub_total_data})
        else:
            from collections import OrderedDict
            tmp = {}
            for val in aggregations:
                tmp_columns = group_by + [val['op']] if group_by else [val['op']]
                cursor.execute(self.build_row_sql(filters, '', limit, offset, columns=','.join(tmp_columns), group_by=','.join(group_by)), filters['params'])
                agg_data_tmp = dict_fetchall(cursor)

                for row in agg_data_tmp:
                    tmp_key = self.get_key_by_group_fields(row, group_by)
                    field_type = self.report.get_field_type_by_alias(val['alias'])
                    tmp_val = field_type.to_str(row[val['res_field']])
                    tmp_val = {'header': val['header'], 'data': tmp_val}

                    if tmp_key in tmp:
                        tmp[tmp_key]['agg_data'].append(tmp_val)
                    else:
                        tmp[tmp_key] = {'agg_caption': tmp_key, 'agg_data': [tmp_val], 'rep_data': [], 'sub_total_data': []}

            # start sub totals

            tmp_sub_totals = {}
            for val in sub_totals:
                tmp_columns = group_by + [val['op']] if group_by else [val['op']]
                cursor.execute(self.build_row_sql(filters, '', limit, offset, columns=','.join(tmp_columns), group_by=','.join(group_by)), filters['params'])
                data_tmp = dict_fetchall(cursor)

                for row in data_tmp:
                    tmp_key = self.get_key_by_group_fields(row, group_by)
                    field_type = self.report.get_field_type_by_alias(val['alias'])
                    tmp_val = field_type.to_str(row[val['res_field']])

                    if tmp_key in tmp_sub_totals:
                        tmp_sub_totals[tmp_key][val['alias']] = tmp_val
                    else:
                        tmp_sub_totals[tmp_key] = dict()
                        tmp_sub_totals[tmp_key][val['alias']] = tmp_val

            # end sub totals

            for row in rep_data_tmp:
                tmp_key = self.get_key_by_group_fields(row, group_by)

                if tmp_key not in tmp:
                    tmp[tmp_key] = {'agg_caption': tmp_key, 'agg_data': [], 'rep_data': [], 'sub_total_data': []}

                tmp[tmp_key]['rep_data'].append(self.rep_data_row_to_list(row, data_fields))

            if sub_totals:
                for key in tmp_sub_totals:
                    tmp_sub_total_data = tmp_sub_totals[key]
                    res_data = tmp[key]
                    for val in data_fields:
                        res_data['sub_total_data'].append(tmp_sub_total_data[val] if val in tmp_sub_total_data else '')

            tmp_res = OrderedDict(sorted(tmp.items(), key=lambda t: t[0]))
            for key, val in tmp_res.items():
                result.append(val)

            result.append({'agg_caption': None, 'agg_data': agg_data, 'rep_data': None})

        return result

    def extract_report_data_with_stats(self, aggregations, filters, order_by, group_by, data_fields, data_as_list, limit=None, offset=None):
        data = self.extract_data(filters, order_by, limit, offset)
        total = self.extract_data_count({'filter': '', 'params': []}, '', None, None)['rec_count']
        filtered = self.extract_data_count(filters, '', None, None)['rec_count']

        return {'data': data, 'total': total, 'filtered': filtered}


def dict_fetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]