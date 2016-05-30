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

from rabbit_mq.rabbit import rabbit_app
from WebApp.settings.celery_cron import CELERY_TIMEZONE, CELERYBEAT_SCHEDULE

rabbit_app.conf.update(CELERYBEAT_SCHEDULE=CELERYBEAT_SCHEDULE, CELERY_TIMEZONE=CELERY_TIMEZONE)

if __name__ == '__main__':
    rabbit_app.start()