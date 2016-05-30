#!/usr/bin/env python
"""

"""

from treelib import Tree
from ..writer.xls import ReportXlsWriter
from ..definition.field import ReportDefinitionField
from .. import report_registry


__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, Vyruchayka"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportBuilder():
    def __init__(self, report_definition, report=None, custom_where_clause=None):
        self.report_definition = report_definition
        self.custom_where_clause = custom_where_clause

        if report is None:
            self.report = report_registry.get_report_by_alias(self.report_definition.alias)
        else:
            self.report = report

    def build_filters(self):
        pass

    def build_aggregations(self):
        pass

    def build_order_by(self):
        pass

    def build_sub_total(self, sub_total_fields):
        pass

    def rep_data_row_to_list(self, row, fields):
        result = list()

        for field in fields:
            if field != '':
                field_type = self.report.get_field_type_by_alias(field)
                if type(row) is dict:
                    result.append(field_type.to_str(row[field]) if field_type is not None else row[field])
                else:
                    result.append(field_type.to_str(getattr(row, field)) if field_type is not None else getattr(row, field))
            else:
                result.append('')

        return result

    def dict_data(self, dict_in, fields):
        result = dict()

        for field in fields:
            if field != '':
                field_type = self.report.get_field_type_by_alias(field)
                result[field] = field_type.to_str(dict_in[field]) if field_type is not None else dict_in[field]
            else:
                result[field] = ''

        return result

    def rep_data_to_list(self, data, fields):
        result = list()

        for row in data:
            result.append(self.rep_data_row_to_list(row, fields))

        return result

    def get_rep_data_with_stats(self, data_as_list=False, limit=None, offset=None, convert_data=True):
        aggregations = self.build_aggregations()
        filters = self.build_filters()
        order_by = self.build_order_by()
        group_by = self.report_definition.group_by_fields

        header_tree = self.build_header_tree()
        leaves_fields = self.get_leaves_fields_from_tree(header_tree)

        data_fields = list()
        for val in leaves_fields:
            data_fields.append(val.alias)

        stats = self.extract_report_data_with_stats(aggregations, filters, order_by, group_by,
                                                    data_fields, data_as_list, limit, offset)
        tmp_list = list()

        for val in stats['data']:
            tmp_data = self.dict_data(val, data_fields) if convert_data else val
            tmp_list.append(tmp_data if not data_as_list else tmp_data.values())

        stats['data'] = tmp_list

        return stats

    def extract_data(self, filters, order_by, limit, offset):
        pass

    def get_key_by_group_fields(self, row, group_by_fields):
        res = ''

        for field in group_by_fields:
            res += ' ' + str(row[field] if isinstance(row, dict) else getattr(row, field))

        return res

    def get_report_data(self):
        aggregations = self.build_aggregations()
        filters = self.build_filters()
        order_by = self.build_order_by()
        group_by = self.report_definition.group_by_fields

        header_tree = self.build_header_tree()
        leaves_fields = self.get_leaves_fields_from_tree(header_tree)

        data_fields = list()
        sub_total_fields = list()
        for val in leaves_fields:
            data_fields.append(val.alias)
            field = self.report.get_field_by_alias(val.alias)
            if field.need_sub_total and val.alias not in sub_total_fields:
                sub_total_fields.append(val.alias)

        sub_totals = self.build_sub_total(sub_total_fields)

        report_data = self.build_report_data(aggregations, filters, order_by, group_by, data_fields, sub_totals=sub_totals)

        return report_data

    def generate_report(self, report_dir=None):
        aggregations = self.build_aggregations()
        filters = self.build_filters()
        order_by = self.build_order_by()
        group_by = self.report_definition.group_by_fields

        header_tree = self.build_header_tree()
        header_fields = self.get_fields_from_tree(header_tree)
        leaves_fields = self.get_leaves_fields_from_tree(header_tree)

        data_fields = list()
        sub_total_fields = list()
        for val in leaves_fields:
            data_fields.append(val.alias)
            field = self.report.get_field_by_alias(val.alias)
            if field.need_sub_total and val.alias not in sub_total_fields:
                sub_total_fields.append(val.alias)

        sub_totals = self.build_sub_total(sub_total_fields)
        report_data = self.build_report_data(aggregations, filters, order_by, group_by, data_fields, sub_totals=sub_totals)

        writer = ReportXlsWriter(self.report_definition.alias, self.report_definition.header, header_fields,
                                 report_data, report_dir, report_sub_header=self.report_definition.sub_header)
        file_path = writer.write_to_file()

        return file_path

    def build_html_header(self):
        header_tree = self.build_header_tree()

        result = []
        tree_depth = header_tree.depth()
        for i in range(0, tree_depth+1):
            result.append([])

        html_header_tree = self.__prepare_tree_for_html_header(header_tree, header_tree.root, 0, 1, result)

        html_header = ''

        for item in html_header_tree[1:]:
            row_header = ''
            for field in item:
                row_header += '<th colspan={0} rowspan={1} style="text-align: center; vertical-align: middle">{2}</th>'.format(field.col_span, field.row_span, field.header)
            html_header += '<tr>{0}</tr>'.format(row_header)

        return html_header

    def build_header_tree(self):
        header_tree = Tree()

        root_field = ReportDefinitionField()
        root_field.alias = 'root'
        root_field.header = 'Root'
        root_field.sub_fields = self.report_definition.fields

        self.__build_header_tree(header_tree, None, root_field)
        self.__prepare_header_data(header_tree, header_tree.get_node(header_tree.root))

        return header_tree

    def get_fields_from_tree(self, header_tree):

        res_fields = list()

        for node in header_tree.is_branch(header_tree.root):
            res_fields.append(header_tree.get_node(node).data)

        return res_fields

    def get_leaves_fields_from_tree(self, header_tree):
        leaves_fields = list()

        for leave in header_tree.leaves(header_tree.root):
            leaves_fields.append(header_tree.get_node(leave).data)

        return leaves_fields

    def __build_header_tree(self, header_tree, parent, node):

        if parent is None:
            tmp_node = header_tree.create_node(data=node)
        else:
            tmp_node = header_tree.create_node(parent=parent.tag, data=node)

        for child in node.sub_fields:
            self.__build_header_tree(header_tree, tmp_node, child)

        return tmp_node

    def __prepare_header_data(self, header_tree, node):
        tmp_tree = header_tree.subtree(node.tag)
        node.data.col_span = len(tmp_tree.leaves(node.tag))

        if node.is_root():
            node.data.row_span = 1
        else:
            parent_node = header_tree.parent(node.tag)
            parent_tree = header_tree.subtree(parent_node.tag)
            node.data.row_span = parent_tree.depth() - tmp_tree.depth()

        for sub_node in tmp_tree.is_branch(node.tag):
            tmp_node = tmp_tree.get_node(sub_node)
            self.__prepare_header_data(header_tree, tmp_node)

        field = self.report.get_field_by_alias(node.data.alias)

        if field is not None:
            node.data.cell_width = field.cell_width

        return node

    def __prepare_tree_for_html_header(self, tree, node, level, row_span, result):
        node_data = tree.get_node(node).data
        result[level + row_span - 1].append(node_data)

        for tmp_node in tree.is_branch(node):
            self.__prepare_tree_for_html_header(tree, tmp_node, level + 1, node_data.row_span, result)

        return result

    def build_report_data(self, aggregations, filters, order_by, group_by, data_fields, limit=None, offset=None, sub_totals=None):
        pass

    def extract_report_data_with_stats(self, aggregations, filters, order_by, group_by, data_fields, data_as_list, limit=None, offset=None):
        pass