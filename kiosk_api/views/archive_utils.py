# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound
from Model import Kiosk, UPC, Disk, Slot
from Model.kiosk_calibration import KioskCalibration

__author__ = 'Denis Ivanets (denself@gmail.com)'


def process_database(s, code, db_file):
    engine = create_engine('sqlite:///{}'.format(db_file))
    connection = engine.connect()

    k = s.query(Kiosk).filter(Kiosk.activation_code == code).one()

    disks = get_disk_info(connection, s, k)
    s.add_all(disks)

    slots = get_slot_info(connection, s, k)
    s.add_all(slots)

    calibration = get_calibration_info(connection, s, k)
    s.add(calibration)

    s.commit()


def get_disk_info(connection, s, kiosk):
    """This function retrieves information about disks and returns
    list of Disk objects.
    :param connection: connection to sqlite database
    :param s: server db session object
    :return: list of Disks
    """
    query = "select rfid, upc, state from rfids"
    query_result = connection.execute(query)
    for row in query_result:
        upc = s.query(UPC.upc).filter_by(upc=row['upc']).scalar()
        try:
            disk = s.query(Disk).filter_by(rf_id=row['rfid']).one()
        except NoResultFound:
            disk = Disk()
            disk.rf_id = row['rfid']
            disk.upc_link = upc
        if row['state'] == 'bad':
            disk.state_id = 6
        elif row['state'] == 'out':
            disk.state_id = 10
        disk.company_id = kiosk.company_id
        yield disk


def get_slot_info(connection, s, kiosk):
    """This func retrieves info about slots and disks in those slots.
    Also, if disk in rent, mark in correct way.
    :param connection: connection to sqlite database
    :param s: server db session object
    :return: list of Slots
    """
    query = "select id, rfid, state from slots"
    query_result = connection.execute(query)
    kiosk_id = int(kiosk.id)
    for row in query_result:
        slot_number, rfid, state = row
        try:
            slot = s.query(Slot) \
                .filter(Slot.kiosk_id == kiosk_id) \
                .filter(Slot.number == int(slot_number)).one()
        except NoResultFound:
            slot = Slot()
            slot.kiosk_id = kiosk.id
            slot.number = slot_number
            slot.status_id = 1

        disk = s.query(Disk).get(rfid)
        if disk:
            disk.slot_number = slot_number
            disk.kiosk_id = kiosk_id
            slot.disk = None
            if disk.state_id in (0, 6):
                slot.disk = disk

        # Mark said not to mark slots as bad, even is they are
        # if row['slot_state'] == 'bad':
        #     slot.status_id = 6
        yield slot


def get_calibration_info(connection, s, kiosk):
    """This func retrieves calibration info and stores it.
    :param connection: connection to sqlite database
    :param s: server db session object
    :return: calibration object with proper parameters
    """
    calibration = kiosk.calibration or KioskCalibration(kiosk=kiosk)
    # calibration.kiosk = kiosk.id
    calibration_parameters = [
        'top_offset', 'bottom_offset', 'exchange_offset', 'back_offset',
        'pulses_per_slot', 'distance1', 'distance2', 'robot_retry',
        'offset2xx', 'offset6xx'
    ]

    query = "select value from info where variable like 'KioskID'"
    kiosk_alias = connection.execute(query).fetchall()
    try:
        calibration.alias = kiosk_alias[0][0]
    except:
        calibration.alias = ''

    query = "select value from config where variable like '{}'"
    for parameter in calibration_parameters:
        r = connection.execute(query.format(parameter)).fetchall()
        try:
            # Here must be a value like r == [(u'200',)]
            r = float(r[0][0])
        except:
            r = None
        calibration.__setattr__(parameter, r)

    return calibration


if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker

    _db_file = '/home/denis/Work/WebApp/mkc_f403.db'
    _engine = create_engine('sqlite:///{}'.format(_db_file))
    _connection = _engine.connect()
    _s = sessionmaker(bind=create_engine('postgresql://kiosk:kiosk@77.120.98.132:5432/kiosk_global_dev'))()
    _k = _s.query(Kiosk).filter(Kiosk.activation_code == 'MdOgL9HL').one()
    process_database(_s, 'MdOgL9HL', _db_file)
    # s.commit()
    # list(get_slot_info(connection, _s, _k))