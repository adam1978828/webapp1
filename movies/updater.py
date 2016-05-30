#!/usr/bin/env python
"""

"""

from django.conf import settings
from Model import UpdateMoviesStatsAlt
from parse_csv_alt import update_db, update_poster_image_file_hash

import datetime

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


DOWNLOAD_HOUR = 12
DOWNLOAD_EACH_DAYS = 7
ACTION_TIMEOUT = 24


def load_movie_data(user_id, force_start):
    db_session = settings.SESSION()
    load = db_session.query(UpdateMoviesStatsAlt).filter(UpdateMoviesStatsAlt.dt_end == None).first()

    if load:
        if (load.dt_modify + datetime.timedelta(hours=ACTION_TIMEOUT)) < datetime.datetime.utcnow():
        # if load.dt_modify < datetime.datetime.utcnow():
            load.dt_end = datetime.datetime.utcnow()
            load.status = -load.status.id
            # db_session.add(load)
            # db_session.commit()
        else:
            return

    force_start = force_start or (db_session.query(UpdateMoviesStatsAlt).count() == 0)
    can_run = force_start
    if not force_start:
        latest_load = db_session.query(UpdateMoviesStatsAlt).filter(UpdateMoviesStatsAlt._status_id == 0).\
            order_by(UpdateMoviesStatsAlt.dt_start.desc()).first().dt_start
        next_load = get_next_load_dt(latest_load)
        can_run = datetime.datetime.now() >= next_load

    if not can_run:
        return

    data_load = UpdateMoviesStatsAlt(user_id=user_id, dt_start=datetime.datetime.utcnow())
    db_session.add(data_load)
    db_session.commit()
    try:
        update_db(db_session, data_load)
        status_id = 0
        error_text = None
    except Exception as e:
        status_id = -data_load.status.id
        error_text = str(e)

    data_load.dt_end = datetime.datetime.utcnow()
    data_load.status = status_id
    data_load.error_text = error_text

    db_session.add(data_load)
    db_session.commit()


def get_next_load_dt(last_load_dt):

    next_load = last_load_dt.replace(hour=0, minute=0, second=0)
    next_load = next_load + datetime.timedelta(days=DOWNLOAD_EACH_DAYS) + datetime.timedelta(hours=DOWNLOAD_HOUR)

    return next_load


def update_image_hash(user_id, force_start):
    db_session = settings.SESSION()
    load = db_session.query(UpdateMoviesStatsAlt).filter(UpdateMoviesStatsAlt.dt_end == None).first()

    if load:
        if (load.dt_modify + datetime.timedelta(hours=ACTION_TIMEOUT)) < datetime.datetime.utcnow():
        # if load.dt_modify < datetime.datetime.utcnow():
            load.dt_end = datetime.datetime.utcnow()
            load.status = -load.status.id
            # db_session.add(load)
            # db_session.commit()
        else:
            return

    force_start = force_start or (db_session.query(UpdateMoviesStatsAlt).count() == 0)
    can_run = force_start
    if not force_start:
        latest_load = db_session.query(UpdateMoviesStatsAlt).filter(UpdateMoviesStatsAlt._status_id == 0).\
            order_by(UpdateMoviesStatsAlt.dt_start.desc()).first().dt_start
        next_load = get_next_load_dt(latest_load)
        can_run = datetime.datetime.now() >= next_load

    if not can_run:
        return

    data_load = UpdateMoviesStatsAlt(user_id=user_id, dt_start=datetime.datetime.utcnow(), _status_id=4)
    db_session.add(data_load)
    db_session.commit()
    try:
        update_poster_image_file_hash(db_session, data_load)
        status_id = 0
        error_text = None
    except Exception as e:
        status_id = -data_load.status.id
        error_text = str(e)

    data_load.dt_end = datetime.datetime.utcnow()
    data_load.status = status_id
    data_load.error_text = error_text

    db_session.add(data_load)
    db_session.commit()