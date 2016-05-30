# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import ntpath
import os
import re

from django.conf import settings
import pika
import requests

from WebApp.utils import splitext

__author__ = 'Denis Ivanets (denself@gmail.com)'
re_pattern = r'^(.*)\([ \'&0-9a-zA-Z\.\,\\/-]*\)$'


def init_logger():
    """Helps to init logger for update_csv functions
    :return: logger object
    :rtype: logging.Logger
    """
    name = 'movie_update'
    new_log = logging.getLogger(name)
    new_log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s]%(levelname)-5s[%(module)s.%(funcName)s] %(message)s')
    new_log.handlers = []

    handler = logging.FileHandler(os.path.join(settings.LOGS_DIR, '%s_info.log' % name), 'a')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    new_log.addHandler(handler)

    handler = logging.FileHandler(os.path.join(settings.LOGS_DIR, '%s_warn.log' % name), 'a')
    handler.setFormatter(formatter)
    handler.setLevel(logging.WARNING)
    new_log.addHandler(handler)

    return new_log


def send_message(message):
    """Sends message to RabbitMQ to push it to update center.
    :param message: Message to send.
    :type message: unicode
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=str('localhost')))
    properties = pika.BasicProperties(content_type='text/html', delivery_mode=1)
    channel = connection.channel()
    channel.exchange_declare(exchange='logs', type='fanout')
    channel.basic_publish(exchange='logs', routing_key='', body=message, properties=properties)
    connection.close()


def compare_optimize(name):
    """ Optimizes movie name from csv file to
        `easy for compare` form
    :param name: Movie name
    :type name: unicode
    :return: Optimized for tmdb search result movie name and csv file
        movie name comparison
    :rtype: unicode
    """
    if re.search(re_pattern, name):
        if re.search(re_pattern, name).groups()[0]:
            name = re.search(re_pattern, name).groups()[0]
    result = name.lower().replace('[', '(').replace(']', ')')
    if result.startswith('the '):
        result = result.replace('the ', '', 1)
    if result.startswith('a '):
        result = result.replace('a ', '', 1)
    result = result.replace(',', '').replace('.', '')
    result = result.replace('one ', '1 ').replace('ten ', '10 ').replace('two ', '2')
    result = result.replace(' ', '')
    result = result.replace('\'', '').replace('’', '')
    result = result.replace('#', '').replace('-', '').replace(':', '')
    result = result.replace('•', '').replace('°', '')
    result = result.replace('²', '2').replace('½', '1/2')
    result = result.replace('í', 'i')
    return result


def search_optimize(name):
    """ Optimizes movie name from csv file to
        `easy for search and compare` form
    :param name: Movie name
    :type name: unicode
    :return: Optimized for tmdb search movie name
    :rtype: unicode
    """
    if re.search(re_pattern, name):
        name = re.search(re_pattern, name).groups()[0]
    result = name.replace('[', '(').replace(']', ')')
    return result


def download_archive():
    """Downloads and saves archive with csv from
    http://www.hometheaterinfo.com/download/{file_type}.zip
    dvd_csv - for the file with the whole db;
    new_csv - for the file with weekly updates only;
    :return: path to downloaded archive
    :rtype: unicode
    """
    file_type = 'dvd_csv'
    file_name = '{}.zip'.format(file_type)
    file_path = os.path.join(settings.TEMP_DIR, file_name)
    file_link = 'http://www.hometheaterinfo.com/download/{}'.format(file_name)

    response = requests.get(file_link, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
        f.close()

    return file_path

def download_from_omdb():
    API_KEY = u'29ef34cf'
    link = u'http://img.omdbapi.com/?apikey={API_KEY}&'.format(API_KEY)
    response = requests.get(link, stream=True)


def extract_zip_archive(archive_path):
    """Helper, that extracts required file from downloaded zip archive
    :param archive_path: Path to downloaded archive.
    :type archive_path: unicode
    :return: path to extracted csv file
    :rtype: unicode
    """
    from zipfile import ZipFile

    archive_name, archive_type = splitext(ntpath.basename(archive_path))
    csv_name = '{}.txt'.format(archive_name)
    csv_path = os.path.join(ntpath.dirname(archive_path), csv_name)

    zp = ZipFile(archive_path, 'r')
    zp.extract(csv_name, ntpath.dirname(archive_path))
    zp.close()
    os.remove(archive_path)
    return csv_path