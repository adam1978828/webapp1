#!/usr/bin/env python
"""

"""

import os
import tarfile

from .analyzer import SQLiteDBCompare, SQLiteDBCompareItem

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


ROOT_FOLDER = 'D:\\KIOSK_LOCAL_DBS\\local_dbs'
OUTPUT_FOLDER = 'D:\\KIOSK_LOCAL_DBS\\results'


def analyse_folder(skip_extract=True):
    print('GLOBAL ANALYSIS!')
    print('GET KIOSK DIRS...')

    dirs = os.listdir(ROOT_FOLDER)
    kiosk_dict = {}
    total_dirs = len(dirs)
    analyzed_dirs = 1

    print('TOTAL DIRS: {0}'.format(total_dirs))
    print('PREPARE DIRS...')

    for kiosk_dir in dirs:
        print('PREPARING DIR {0} ({1} of {2})'.format(kiosk_dir, analyzed_dirs, total_dirs))

        kiosk_id = kiosk_dir.replace('k_', '')
        db_root_dir = os.path.join(ROOT_FOLDER, kiosk_dir)
        db_dirs = os.listdir(db_root_dir)

        kiosk_dict[kiosk_id] = []

        for db_dir in db_dirs:
            res_dir = os.path.join(db_root_dir, db_dir)
            res_file = os.path.join(res_dir, 'local.db')

            if not skip_extract:
                tfile = tarfile.open(os.path.join(res_dir, 'db.tar.gz'), 'r:gz')
                tfile.extract('local.db', res_dir)

            kiosk_dict[kiosk_id].append(res_file)

        analyzed_dirs += 1

    analyzed_dirs = 1
    print('START DIR ANALYSIS...')

    global_csv_results = open(os.path.join(OUTPUT_FOLDER, 'results.csv'), 'w')
    sql_results = open(os.path.join(OUTPUT_FOLDER, 'results.sql'), 'w')

    sql_results.write('insert into global_inventory_check \n')
    sql_results.write('(kiosk_id, slot_number, status_id, rf_id, upc, state_id, before_after)\n values')

    for k, v in kiosk_dict.iteritems():
        print('ANALYZING DIR k_{0} ({1} of {2})'.format(k, analyzed_dirs, total_dirs))

        if len(v) != 2:
            print('DIR k_{0} SKIPPED'.format(k))
            analyzed_dirs += 1
            continue

        result = compare_local_dbs(v[0], v[1], k)

        for val in result:
            val_list = [k] + val[0] + [1]
            global_csv_results.write(','.join(map(str, val_list)) + '\n')
            sql_results.write('({0}, {1}, {2}, "{3}", "{4}", {5}, {6}),\n'.format(*val_list))

            val_list = [k] + val[1] + [2]
            global_csv_results.write(','.join(map(str, val_list)) + '\n')
            sql_results.write('({0}, {1}, {2}, "{3}", "{4}", {5}, {6}),\n'.format(*val_list))

        analyzed_dirs += 1

        print('DIR k_{0} ANALYZING FINISHED'.format(k))
    global_csv_results.close()

    print('GLOBAL ANALYSIS HAS BEEN SUCCESSFULLY FINISHED!')


def compare_local_dbs(db1_path, db2_path, kiosk_id):
    custom_sql = 'select s.slot_number, s.status_id, d.rf_id, d.upc, d.state_id from k_slot s ' \
                 'left join disk d on s.id=d.slot_id and s.kiosk_id=d.kiosk_id where s.kiosk_id={0} order by s.slot_number asc'.format(kiosk_id)
    compare_item = SQLiteDBCompareItem('k_slot', 'slot_number', ['status_id', 'rf_id', 'upc', 'state_id'], custom_sql)

    output_dir = os.path.join(OUTPUT_FOLDER, 'kiosk_{0}'.format(kiosk_id))
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    comparer = SQLiteDBCompare(db1_path, db2_path, output_dir, [compare_item])
    result = comparer.run()
    return result[compare_item]