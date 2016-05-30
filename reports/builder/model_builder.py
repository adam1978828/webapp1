#!/usr/bin/env python
"""

"""

from .base import ReportBuilder
from functools import reduce

import operator

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, Vyruchayka"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class DjangoModelReportBuilder(ReportBuilder):

    def build_filters(self):
        filters = list()
        join_operation = operator.and_ if self.report_definition.filter_operation == 'and' else operator.ior

        for val in self.report_definition.filters:
            field = self.report.get_field_by_alias(val.alias)

            if field is not None and field.filters is not None:
                tmp_data = field.field_type.from_str(val.data)
                tmp_filter = field.filters.build_filter(tmp_data, val.op_alias)

                if tmp_filter is not None:
                    filters.append(tmp_filter)

        return reduce(join_operation, filters) if filters else filters

    def build_aggregations(self):
        aggregations = list()

        for val in self.report_definition.aggregations:
            field = self.report.get_field_by_alias(val.alias)

            if field is not None and field.aggregations is not None:
                agg_op = field.get_aggregation(val.agg_alias)
                aggregations.append({'op': agg_op.build_aggregation(field.model_field_name),
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
                order_by_fields.append(order_by.build_order_by_field(field.model_field_name))

        return order_by_fields

    def extract_data(self, filters, order_by, limit, offset):
        if filters:
            rep_data_tmp = self.report.model.objects.filter(filters).order_by(*order_by)
        else:
            rep_data_tmp = self.report.model.objects.all().order_by(*order_by)

        if limit is not None and offset is not None:
            rep_data_tmp = rep_data_tmp[offset:limit]
        elif limit is not None:
            rep_data_tmp = rep_data_tmp[:limit]
        elif offset is not None:
            rep_data_tmp = rep_data_tmp[offset]

        return rep_data_tmp

    def build_report_data(self, aggregations, filters, order_by, group_by, data_fields, limit=None, offset=None):
        result = list()
        agg_data = list()

        for val in aggregations:
            if filters:
                agg_data_tmp = self.report.model.objects.filter(filters).aggregate(val['op'])
            else:
                agg_data_tmp = self.report.model.objects.aggregate(val['op'])

            field_type = self.report.get_field_type_by_alias(val['alias'])
            tmp_val = field_type.to_str(agg_data_tmp[val['res_field']])

            agg_data.append({'header': val['header'], 'data': tmp_val})

        rep_data_tmp = self.extract_data(filters, order_by, limit, offset)

        if not group_by:
            result.append({'agg_caption': None, 'agg_data': agg_data, 'rep_data': self.rep_data_to_list(rep_data_tmp, data_fields)})
        else:
            result.append({'agg_caption': None, 'agg_data': agg_data, 'rep_data': None})

            tmp = {}
            for val in aggregations:
                if filters:
                    agg_data_tmp = self.report.model.objects.values(*group_by).filter(filters).annotate(val['op'])
                else:
                    agg_data_tmp = self.report.model.objects.values(*group_by).annotate(val['op'])

                for row in agg_data_tmp:
                    tmp_key = self.get_key_by_group_fields(row, group_by)
                    field_type = self.report.get_field_type_by_alias(val['alias'])
                    tmp_val = field_type.to_str(row[val['res_field']])
                    tmp_val = {'header': val['header'], 'data': tmp_val}
                    if tmp_key in tmp:
                        tmp[tmp_key]['agg_data'].append(tmp_val)
                    else:
                        tmp[tmp_key] = {'agg_caption': tmp_key, 'agg_data': [tmp_val], 'rep_data': []}

            for row in rep_data_tmp:
                tmp_key = self.get_key_by_group_fields(row, group_by)

                if tmp_key not in tmp:
                    tmp[tmp_key] = {'agg_caption': tmp_key, 'agg_data': [], 'rep_data': []}

                tmp[tmp_key]['rep_data'].append(self.rep_data_row_to_list(row, data_fields))

            for key in tmp.keys():
                result.append(tmp[key])

        return result

    def extract_report_data_with_stats(self, aggregations, filters, order_by, group_by, data_fields, data_as_list, limit=None, offset=None):
        data = self.extract_data(filters, order_by, limit, offset)
        total = self.extract_data({'filters': '', 'params': []}, None, None, None)
        filtered = self.extract_data(filters, [], None, None)

        return {'data': data, 'total': total.count(), 'filtered': filtered.count()}