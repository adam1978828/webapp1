# -*- coding: utf-8 -*-
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from sqlalchemy.orm.exc import NoResultFound

from Model import *
from WebApp.utils import alchemy_to_json, alchemy_list_to_json


__author__ = 'D.Ivanets'


@require_POST
@csrf_exempt
def data_download(request):
    """This view called when kiosk tries to download db data at first time.
    """
    data_in = json.loads(request.body)

    try:
        kiosk_activation_code = data_in.get(u'activation_code', '')
        kiosk = request.db_session.query(Kiosk)\
            .filter_by(activation_code=kiosk_activation_code).one()
        request.kiosk = kiosk

        data = {
            u'uuid': kiosk.uuid,
            u'error_code': 0,
            u'error_message': u'Everything successfully downloaded',
            u'data': {
                u'c_kiosk': [alchemy_to_json(kiosk)],
                u'c_company': [alchemy_to_json(kiosk.company)],
            },
            u'dt_sync': request.cur_datetime.isoformat(),
        }

        data[u'data'].update(get_data_to_send(request))

        kiosk.dt_sync = request.cur_datetime
    except NoResultFound:
        data = {
            u'error_code': 1,
            u'error_message': u'Incorrect activation code.',
        }
    except Exception as ex:
        data = {
            u'error_code': 2,
            u'error_message': ex.message,
        }
    print data[u'error_message']
    return JsonResponse(data)


def get_data_to_send(request):
    """ Helps to dump DB data into json format to send it to kiosk
    """
    # list of tables, that should be uploaded to kiosk.
    table_list = [
        # e_ tables - static information, used in all kiosk.
        DealType, DiskCondition, DiskFormat, Language, MovieGenre,  # UserType,
        MovieGenreTranslation, MovieRating, CardStatus, PreauthMethod,
        NoInternetOperation, SlotStatus, Timezone, CouponType,
        # d_ tables - information about movies (and games)
        Movie, MovieMovieGenre, MovieTranslation, UPC, UpcMovie, UpcSound,
        UpcSubtitle, User, TariffPlan, TariffValue, Disk, Card, Deal,
        CompanyUpcTariffPlan, FeaturedMovie, VideoFile, Coupon,
        KioskCalibration, KioskSettings, KioskSettingsToLanguage, Slot,
        VideoSchedule, KioskSkipDates, KioskSkipWeekdays, CouponUsageInfo,
        KioskReview, KioskReviewSlot,
    ]

    data = {}

    # Here we query info from tables one by one
    for cls in table_list:
        print cls,
        query = request.db_session.query(cls)

        # Applying rules for synchronizing data
        print 'Query',
        for clause in cls.sync_filter_rules:
            query = query.filter(clause(request))
        # Applying rules for downloading data
        for clause in cls.load_filter_rules:
            query = query.filter(clause(request))

        if hasattr(cls, 'is_active'):
            query.filter_by(is_active=True)

        data.update(alchemy_list_to_json(query.all()))
        print 'Done'

    return data
