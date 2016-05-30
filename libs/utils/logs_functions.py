# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os

from django.conf import settings


__author__ = 'Denis Ivanets (denself@gmail.com)'


def init_logger(name):
    """Helps to init logger for update_csv functions
    :param name: Name of logger
    :type name: unicode
    :return: logger object
    :rtype: logging.Logger
    """

    new_log = logging.getLogger(name)
    new_log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s]%(levelname)-5s[%(module)s.%(funcName)s] %(message)s')
    new_log.handlers = []

    handler = logging.FileHandler(os.path.join(settings.LOGS_DIR, '{}.log'.format(name)), 'a')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    new_log.addHandler(handler)

    return new_log