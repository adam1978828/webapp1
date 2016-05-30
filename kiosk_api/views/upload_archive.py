# -*- coding: utf-8 -*-
import logging
import uuid
import os
import tarfile
from langdetect import detect

from sqlalchemy import create_engine

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from sqlalchemy.orm.exc import NoResultFound
from kiosk_api.utils import http_auth_require, save_file
from libs.utils.logs_functions import init_logger

from libs.validators.core import json_response_content
from libs.utils.string_functions import remove_multilingual_words, filter_chars

from Model import MovieGenreTranslation, Slot
from Model import Kiosk, Disk, UPC, Movie, MovieGenre, MovieTranslation, Language
from Model import MovieMovieGenre, Currency
from .archive_utils import process_database


__author__ = 'D.Kalpakchi, D.Ivanets'


temp_dir = settings.TEMP_DIR
log = init_logger(u'process_archive')


@require_POST
@csrf_exempt
@http_auth_require
def upload_archive(request):
    """This function processes archive with disk data
    from old kiosk software.
    >>> import requests
    >>> host = 'http://66.6.127.167/kiosk_api/upload/archive/'
    >>> lo_host = 'http://localhost:8000/kiosk_api/upload/archive/'
    >>> archive = open('/home/denis/Work/WebApp/mkc.db.tar.gz', 'rb')
    >>> auth = 'denself@gmail.com', '1234Comp'
    >>> files = [('archive', ('mkc.db.tar.gz', archive, 'application/x-gzip'))]
    >>> res = requests.post(url=host, files=files,
    ...                     auth=auth, data={'kioskid': ''})
    >>> print res.text
    """
    log.info("Getting kioskid and archive file from request")
    code = request.POST.get('kioskid', '')
    if not code:
        return JsonResponse(json_response_content('error', 'No kiosk code given'))

    archive = request.FILES.get('archive', None)
    if not archive:
        return JsonResponse(json_response_content('error', 'No archive given'))

    # form paths to required files.
    temp_archive_dir = os.path.join(temp_dir, 'archives', uuid.uuid1().hex)
    temp_archive_path = os.path.join(temp_archive_dir, archive.name)

    log.info("Saving archive to filesystem {}".format(temp_archive_path))
    save_file(archive, temp_archive_path)

    log.info("Extracting DB from archive")
    db_file_path = extract_db_from_archive(temp_archive_path)
    if not db_file_path:
        return JsonResponse(json_response_content('error', 'No db given'))

    log.info("Start processing database")
    try:
        process_database(request.db_session, code, db_file_path)
    except Exception, e:
        log.error("DB processing: {}".format(e.message))
        print e
        return JsonResponse(json_response_content('error', 'Error during DB processing'),
                            {'exception': e.message, 'err_co': 3})
    # import shutil
    # shutil.rmtree(temp_archive_dir)
    return HttpResponse('OK')


def extract_db_from_archive(archive_path):
    """Extracts all files from provided archive to the parent folder
    and removes archive file.

    :param archive_path: Path to archive
    :return: Path to extracted database.
    """
    temp_archive_dir = os.path.dirname(archive_path)

    # Open archive
    tar = tarfile.open(archive_path)
    # Get DB name and path
    tar_content = tar.getnames()
    if not tar_content:
        return None
    db_file_name = tar_content[0]
    db_file_path = os.path.join(temp_archive_dir, db_file_name)
    # Extract DB
    tar.extractall(path=temp_archive_dir)
    tar.close()
    # Remove db
    os.remove(archive_path)
    return db_file_path


def process_database_old(s, code, db_file):
    log.info('Create connection to sqlite db')
    engine = create_engine('sqlite:///{}'.format(db_file))
    connection = engine.connect()

    k = s.query(Kiosk).filter(Kiosk.activation_code == code).one()
    # english = s.query(Language).filter_by(short_name='en').first()

    # log.info('Get kiosk Alias')
    # print "---------------- INFO TABLE -------------------"
    # result = connection.execute('SELECT * FROM info')
    # for row in result:
    #     if row['variable'] == 'KioskID':
    #         k.settings.alias = row['value']
    #         print "Alias was set successfully."
    # s.add(k)
    # s.flush()
    # print "-----------------------------------------------\n"

    print "---------------- SLOTS + RFIDS TABLE -------------------"
    log.info('Get disks and slots data')
    result = connection.execute(
        """
        SELECT rfids.rfid AS rfid, upc, title, genre, rfids.state AS disk_state,
               slots.id AS slot_id, slots.rfid AS slot_rfid,
               slots.state AS slot_state, rank
        FROM rfids LEFT OUTER JOIN slots ON rfids.rfid = slots.rfid
        """
    )

    log.info('Save disks and slots data')
    for row in result:
        # Getting slot from DB or creating a new one, if it doesn't exists
        try:
            slot = s.query(Slot)\
                .filter(Slot.kiosk == k)\
                .filter(Slot.number == row['slot_id']).one()
        except NoResultFound:
            slot = Slot()
            slot.kiosk_id = k.id
            slot.number = row['slot_id']
            slot.status_id = 1
        if row['slot_state'] == 'bad':
            slot.status_id = 6
        try:
            upc = s.query(UPC).filter_by(upc=row['upc']).one()
        except NoResultFound:
            upc = None

        try:
            disk = s.query(Disk).filter_by(rf_id=row['rfid']).one()
        except NoResultFound:
            disk = Disk(row['rfid'], upc)
            disk.company_id = k.company_id
            if row['disk_state'] == 'bad':
                disk.state_id = 6
            if disk.no_errors():
                s.add(disk)
                s.flush()
            else:
                continue
        if row['rfid'] == row['slot_rfid']:
            disk.slot = slot

        s.add(slot)
        s.flush()
    print "------------------------------------------------\n"

    log.info('Save kiosk configurations')
    print "---------------- CONFIG TABLE -------------------"
    result = connection.execute('select * from config')
    settings_mapper = {
        'terms_and_conditions': 'terms',
        'sale_convert_days': 'sale_convert_days',
        'reservation_expiration': 'reservation_expiration_period',
        'max_dvd_out': 'max_disks_per_card',
        'grace_period': 'grace_period',
        'speaker_volume': 'speaker_volume'
    }

    for row in result:
        if row['variable'] in settings_mapper.keys():
            setattr(k.settings, settings_mapper[row['variable']], row['value'])
        elif row['variable'] == 'currency_symbol':
            k.settings.currency = s.query(Currency)\
                .filter_by(symbol=row['value']).first()
        elif row['variable'] == 'language_switch':
            languages = [s.query(Language).filter_by(short_name=x).first()
                         for x in row['value'].split(',')]
            languages = [l for l in languages if l]
            k.settings.languages = languages
    s.add(k)
    s.commit()
    print "-------------------------------------------------\n"


if __name__ == '__main__':
    """This is only an example. Don't actually run this file,
      it will cause to an error.
    """
    import requests
    archive_file = open('/home/denis/Work/WebApp/mkc.db.tar.gz', 'rb')
    # requests.post('http://localhost:8000/kiosk_api/upload/archive/',
    #               files=[('archive', ('mkc.db.tar.gz', archive_file, 'application/x-gzip'))],
    #               auth=('denself@gmail.com', '1234Comp'))
    res = requests.post('http://localhost:8000/kiosk_api/upload/archive/',
                        files=[('archive', ('mkc.db.tar.gz',
                                            open('/home/denis/Work/WebApp/mkc.db.tar.gz', 'rb'),
                                            'application/x-gzip'))],
                        auth=('denself@gmail.com', '1234Comp'), data={'kioskid': ''})
    print res.text