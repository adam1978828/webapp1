# -*- coding: utf-8 -*-

__author__ = 'pavlonevmerzhitskyi'

import json
from pprint import pprint

from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from WebApp.utils import alchemy_list_to_json
from Model import Coupon,Deal


@csrf_exempt
def get_coupon(request):
    """Used for synchronization coupon data between kiosk and server
    """
    if not request.kiosk:
        return HttpResponseForbidden()

    data_in = json.loads(request.body)
    print request.kiosk
    pprint(data_in)

    code = data_in[u'code']

    session = request.db_session
    coupon = session.query(Coupon).filter(Coupon.code == code).all()
    if coupon:
        data_out = {
            'coupon': alchemy_list_to_json(coupon),
        }
    else:
        data_out = {
            'coupon': None
        }
    pprint(data_out)
    return JsonResponse(data_out)

@csrf_exempt
def get_reserv(request):
    """Used for synchronization reservation deals data between kiosk and server
    """
    if not request.kiosk:
        return HttpResponseForbidden()

    data_in = json.loads(request.body)
    print request.kiosk
    pprint(data_in)

    code = data_in[u'code']

    session = request.db_session
    deals = session.query(Deal) \
            .filter(Deal.kiosk_start_id == request.kiosk.id) \
            .filter(Deal.deal_status_id == 241) \
            .filter(Deal.secret_code == code).all()
    if deals:
        data_out = {
            'reserv_deals': alchemy_list_to_json(deals),
        }
    else:
        data_out = {
            'reserv_deals': None
        }
    pprint(data_out)
    return JsonResponse(data_out)