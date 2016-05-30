#!/usr/bin/env python
"""

"""

import sys
import os

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


SITE_ROOT = os.path.dirname(os.path.abspath(os.path.curdir))
sys.path.insert(0, SITE_ROOT)

from celery import Celery
rabbit_app = Celery('rabbit_mq.rabbit', backend='amqp', broker='amqp://')

#STOP CELERY WORKER: ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9


@rabbit_app.task(ignore_result=True, name='rabbit_mq.rabbit.rbbt_load_movie_data',
                 time_limit=172800, soft_time_limit=172800)
def rbbt_load_movie_data(user_id=None, force_start=False):
    from movies.updater import load_movie_data
    load_movie_data(user_id, force_start)


@rabbit_app.task(ignore_result=True, name='rabbit_mq.rabbit.rbbt_update_movie_poster_hash',
                 time_limit=172800, soft_time_limit=172800)
def rbbt_update_movie_poster_hash(user_id=None, force_start=False):
    from movies.updater import update_image_hash
    update_image_hash(user_id, force_start)