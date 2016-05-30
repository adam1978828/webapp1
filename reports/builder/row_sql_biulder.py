#!/usr/bin/env python
"""

"""

from .db_view_builder import DbViewReportBuilder

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, Vyruchayka"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class RowSqlReportBuilder(DbViewReportBuilder):
    def build_row_sql(self, filters, order_by, limit, offset, columns='*', group_by=None):
        pattern = 'select {0} from ({1}) as R2D2'.format(columns, self.report.model)

        if filters['filters'] != '':
            pattern = pattern + ' where ' + filters['filters']

        if order_by != '':
            pattern = pattern + ' order by ' + order_by

        if group_by:
            pattern = pattern + ' group by ' + group_by

        if limit:
            pattern = pattern + ' limit ' + str(limit)

        if offset:
            pattern = pattern + ' offset ' + str(offset)

        return pattern