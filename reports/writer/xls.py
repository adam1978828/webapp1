#!/usr/bin/env python
"""

"""

import datetime
import xlsxwriter

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, Vyruchayka"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class ReportXlsWriter():
    def __init__(self, report_alias, report_header, report_fields, report_data, report_dir=None, report_sub_header=None):
        self.report_alias = report_alias
        self.report_header = report_header
        self.report_sub_header = report_sub_header
        self.report_fields = report_fields
        self.report_data = report_data
        self.report_dir = report_dir if report_dir else ''
        self.file_path = self.get_report_file_path()

    def get_report_file_path(self):
        prefix = self.report_alias if self.report_alias else 'report'
        return '{0}{1}_{2}.xlsx'.format(self.report_dir, prefix, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))

    def write_data_header(self, sheet, row, col, fmt):
        row_offset = row

        for field in self.report_fields:
            #field = ReportDefinitionField()
            res = self.write_data_header_block(sheet, row, col, fmt, field)
            if row_offset < res[0]:
                row_offset = res[0]
            col += field.col_span

        return row_offset

    def write_data_header_block(self, sheet, row, col, fmt, report_field):
        row_offset = row + report_field.row_span - 1
        col_offset = col + report_field.col_span - 1
        res_row = row_offset

        if row == row_offset and col == col_offset:
            if report_field.cell_width is not None:
                sheet.set_column(row, col, width=float(report_field.cell_width))
            else:
                sheet.set_column(row, col, width=8.43)
            sheet.write(row, col, report_field.header, fmt)
        else:
            sheet.merge_range(row, col, row_offset, col_offset, report_field.header, fmt)
        for val in report_field.sub_fields:
            res = self.write_data_header_block(sheet, row_offset+1, col, fmt, val)
            if res_row < res[0]:
                res_row = res[0]
            col += val.col_span

        return res_row, col_offset

    def write_to_file(self):
        book = xlsxwriter.Workbook(self.file_path)
        sheet = book.add_worksheet()

        row_num = 0
        col_num = 0

        header_fmt = book.add_format({
            'bold':     True,
            'align':    'center',
            'valign':   'vcenter',
            #'bg_color': '#0077A6',
        })

        header_fmt.set_text_wrap()
        header_fmt.set_size(16)

        sub_header_fmt = book.add_format({
            'bold':     True,
            'align':    'center',
            'valign':   'vcenter',
            #'bg_color': '#0077A6',
        })

        sub_header_fmt.set_text_wrap()
        sub_header_fmt.set_size(13)

        sheet.merge_range(row_num, col_num, row_num, col_num + 6, self.report_sub_header, header_fmt)
        if self.report_sub_header:
            row_num += 1
            sheet.merge_range(row_num, col_num, row_num, col_num + 6, self.report_header, sub_header_fmt)

        row_num += 2

        # format for cells with data
        common_fmt = book.add_format({
            'bold':     False,
            'border':   1,
            'align':    'left',
            'valign':   'vcenter',
        })

        # format for cells with sub total data
        sub_total_common_fmt = book.add_format({
            'bold':     True,
            'border':   1,
            'align':    'left',
            'valign':   'vcenter',
        })

        # format for aggregation data
        agg_common_fmt = book.add_format({
            'bold':     False,
            'align':    'left',
            'valign':   'vcenter',
        })

        # format for aggregation data
        agg_common__bold_fmt = book.add_format({
            'bold':     True,
            'align':    'left',
            'valign':   'vcenter',
        })

        # format for cells with data
        agg_caption_fmt = book.add_format({
            'bold':     True,
            'align':    'left',
            'valign':   'vcenter',
            'bg_color': '#C0F6D0',
        })

        field_caption_fmt = book.add_format({
            'bold':     True,
            'align':    'center',
            'border':   1,
            'valign':   'vcenter',
            'bg_color': '#C4C4C4',
        })
        field_caption_fmt.set_text_wrap()

        sheet.write(row_num, col_num, 'Date', agg_common__bold_fmt)
        sheet.write(row_num, col_num + 1, datetime.date.today().strftime('%m/%d/%y'), agg_common_fmt)

        row_num += 2

        for data in self.report_data:
            if data['agg_caption'] is not None:
                sheet.merge_range(row_num, col_num, row_num, col_num + len(data['rep_data'][0]) - 1, data['agg_caption'], agg_caption_fmt)
                row_num += 1

            if data['rep_data'] is not None:
                row_num = self.write_data_header(sheet, row_num, col_num, field_caption_fmt)
                row_num += 1
                for val in data['rep_data']:
                    sheet.write_row(row_num, col_num, val, common_fmt)
                    row_num += 1

            if data.get('sub_total_data'):
                sheet.write_row(row_num, col_num, data['sub_total_data'], sub_total_common_fmt)
                row_num += 2

            for agg in data['agg_data']:
                sheet.write(row_num, col_num, agg['header'], agg_common__bold_fmt)
                sheet.write(row_num, col_num + 1, agg['data'], agg_common_fmt)
                row_num += 1

            row_num += 1

        book.close()

        return self.file_path


class ReportXlsOptions(object):
    def __init__(self, add_name=True, add_filters=False, add_grouping_headers=False, add_sorting=False):
        self.add_name = add_name
        self.add_filters = add_filters
        self.add_grouping_headers = add_grouping_headers
        self.add_sorting = add_sorting