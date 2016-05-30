#!/usr/bin/env python
"""

"""

import sqlite3
import os
import datetime

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class SQLiteDBCompareBaseException(Exception):
    def __init__(self, message):
        self.message = message

    def __unicode__(self):
        return self.message


class SQLiteDBCompareTableNotFoundException(SQLiteDBCompareBaseException):
    def __init__(self, table_name, db_file_path):
        self.message = 'Table <<{0}>> does not exist in the DB <<{1}>>'
        self.table_name = table_name
        self.db_file_path = db_file_path

    def __unicode__(self):
        return self.message.format(self.table_name, self.db_file_path)


class SQLiteDBCompareFieldNotFoundException(SQLiteDBCompareBaseException):
    def __init__(self, table_name, column_name, db_file_path):
        self.message = 'Column <<{0}>> does not exists in the table <<{1}>> (DB: {2})'
        self.table_name = table_name
        self.column_name = column_name
        self.db_file_path = db_file_path

    def __unicode__(self):
        return self.message.format(self.column_name, self.table_name, self.db_file_path)


class SQLiteDBCompareDbFileNotExists(SQLiteDBCompareBaseException):
    def __init__(self, db_file_path):
        self.message = 'DB file can not be found by path {0}'
        self.db_file_path = db_file_path

    def __unicode__(self):
        return self.message.format(self.db_file_path)


class SQLiteDBCompareOutputDirNotExists(SQLiteDBCompareBaseException):
    def __init__(self, output_dir):
        self.message = 'Output directory {0} does not exists'
        self.output_dir = output_dir

    def __unicode__(self):
        return self.message.format(self.output_dir)


class SQLiteDBCompareItem(object):
    def __init__(self, table_name, primary_key, compare_fields, custom_sql=None):
        self.table_name = table_name
        self.primary_key = primary_key
        self.compare_fields = compare_fields
        self.custom_sql = custom_sql

    def __unicode__(self):
        return 'Table {0}, Primary Key: {1}, Compare Fields: {2}'.\
            format(self.table_name, self.primary_key, ','.join(self.compare_fields))


class SQLiteDBCompareResult(object):
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.rows_checked = 0
        self.match_failed_count = 0


class SQLiteDBCompare(object):
    def __init__(self, db1_path, db2_path, output_dir, configs):
        self.db1_path = db1_path
        self.db2_path = db2_path
        self.configs = configs
        self.output_dir = output_dir

        self.validate_params()

        self.db1_connection = None
        self.db2_connection = None

        self.init_connections()
        self.output_file = None

    def validate_params(self):
        if not os.path.exists(self.db1_path):
            raise SQLiteDBCompareDbFileNotExists(self.db1_path)

        if not os.path.exists(self.db2_path):
            raise SQLiteDBCompareDbFileNotExists(self.db2_path)

        if not os.path.exists(self.output_dir):
            raise SQLiteDBCompareOutputDirNotExists(self.output_dir)

        if not self.configs:
            raise SQLiteDBCompareBaseException('Compare parameters is not specified!')

        if type(self.configs) is not list:
            raise SQLiteDBCompareBaseException('Compare parameters must be specified as a list!')

        for val in self.configs:
            if type(val) is not SQLiteDBCompareItem:
                raise SQLiteDBCompareBaseException('Compare parameter must be of type {0}'.format(SQLiteDBCompareItem.__class__.__name__))

    def init_connections(self):
        def dict_factory(cursor, row):
            row_elem = dict()
            row_enum = enumerate(cursor.description)

            d = {}
            primary_key_val = None

            for idx, col in row_enum:
                if not primary_key_val:
                    primary_key_val = row[idx]
                else:
                    d[col[0]] = row[idx]
            row_elem[primary_key_val] = d

            return row_elem

        try:
            self.db1_connection = sqlite3.connect(self.db1_path)
            self.db1_connection.row_factory = dict_factory
        except Exception as e:
            raise SQLiteDBCompareBaseException('DB1 {0} connection failed!\nOriginal exception: {1}'.format(self.db1_path, str(e)))

        try:
            self.db2_connection = sqlite3.connect(self.db2_path)
            self.db2_connection.row_factory = dict_factory
        except Exception as e:
            raise SQLiteDBCompareBaseException('DB2 {0} connection failed!\nOriginal exception: {1}'.format(self.db2_path, str(e)))

    def do_compare(self, config):
        # config = SQLiteDBCompareItem('', '', '')
        start_time = datetime.datetime.utcnow()

        self.write_log('START COMPARING\n{0}'.format(config))

        db1_cursor = self.db1_connection.cursor()
        db2_cursor = self.db2_connection.cursor()

        if config.custom_sql is None:
            sql_string = 'select {0} from {1} order by {2}'.format(','.join([config.primary_key] + config.compare_fields), config.table_name, config.primary_key)
        else:
            sql_string = config.custom_sql

        db1_res = db1_cursor.execute(sql_string).fetchall()
        db2_res = db2_cursor.execute(sql_string).fetchall()

        db1_data = dict()
        db2_data = dict()

        for val in db1_res:
            db1_data.update(val)

        for val in db2_res:
            db2_data.update(val)

        result = list()

        for k, v in db1_data.iteritems():
            db1_val = v
            db2_val = db2_data.get(k)
            was_diffs = False

            for k1, v1 in db1_val.iteritems():
                v2 = db2_val.get(k1)

                if v1 != v2:
                    was_diffs = True
                    self.write_log('Key: {0}, Field: {1}, val1: {2}, val: {3}'.format(k, k1, v1, v2))

            if was_diffs:
                db1_tmp = list()
                db2_tmp = list()

                db1_tmp.append(str(k))
                db2_tmp.append(str(k))

                for f in config.compare_fields:
                    tmp_val = db1_val.get(f)
                    #db1_tmp.append(str(tmp_val) if tmp_val is not None else '')
                    db1_tmp.append(tmp_val)

                    tmp_val = db2_val.get(f)
                    #db2_tmp.append(str(tmp_val) if tmp_val is not None else '')
                    db2_tmp.append(tmp_val)

                result.append((db1_tmp, db2_tmp))

        self.write_log('END COMPARING')
        end_time = datetime.datetime.utcnow()

        return result

    def run(self):
        result = dict()
        for conf in self.configs:
            try:
                res_file_path = os.path.join(self.output_dir, '{0}_{1}.log'.format(datetime.datetime.utcnow().strftime('%Y.%m.%d_%H%M%S'), conf.table_name))
                self.output_file = open(res_file_path, 'w')

                result[conf] = self.do_compare(conf)

                self.output_file.close()
                self.output_file = None
            except Exception as e:
                self.write_log(str(e))
                self.output_file.close()
                self.output_file = None

        return result

    def write_log(self, message):
        self.output_file.write(message + '\n')