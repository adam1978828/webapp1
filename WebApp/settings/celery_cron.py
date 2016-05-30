#!/usr/bin/env python
"""

"""

from datetime import timedelta
from celery.schedules import crontab

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


CELERY_TIMEZONE = 'Europe/Kiev'
CELERYBEAT_SCHEDULE = {
    'update-movie-data': {
        'task': 'rabbit_mq.rabbit.rbbt_load_movie_data',
        'schedule': timedelta(minutes=60),
        'args': (None, False)
    },
}