# -*- coding: utf-8 -*-
from datetime import datetime
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
def upload_log_archive(request):
    """This function processes archive with logs. After reboot kiosk tar all
    logs and upload them
    """
    # Check if there a file in request
    archive = request.FILES.get('archive', None)
    if not archive:
        return JsonResponse(json_response_content('error', 'No archive given'))

    # form paths to required files.
    date_folder = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    dir_name = 'k_{}/{}'.format(request.kiosk.id, date_folder)
    temp_archive_dir = os.path.join(temp_dir, 'log_archives', dir_name)
    temp_archive_path = os.path.join(temp_archive_dir, archive.name)

    log.info("Saving archive to filesystem {}".format(temp_archive_path))
    save_file(archive, temp_archive_path)

    # import shutil
    # shutil.rmtree(temp_archive_dir)
    return HttpResponse('OK')

@require_POST
@csrf_exempt
def upload_local_db(request):
    """This function get local db from kiosk on server.
    """
    # Check if there a file in request
    local_db = request.FILES.get('local_db', None)
    if not local_db:
        return JsonResponse(json_response_content('error', 'No local_db given'))

    # form paths to required files.
    date_folder = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    dir_name = 'k_{}/{}'.format(request.kiosk.id, date_folder)
    temp_db_dir = os.path.join(temp_dir, 'local_dbs', dir_name)
    temp_db_path = os.path.join(temp_db_dir, local_db.name)

    log.info("Saving local_db to filesystem {}".format(temp_db_path))
    save_file(local_db, temp_db_path)

    # shutil.rmtree(temp_archive_dir)
    return HttpResponse('OK')