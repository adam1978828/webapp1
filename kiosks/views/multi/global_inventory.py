# -*- coding: utf-8 -*-
from json import loads
from functools import partial
import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed, Http404
from django.shortcuts import render
from sqlalchemy import or_, and_

from Model import Kiosk
from Model import KioskReview, KioskAction, KioskReviewSlot

from libs.validators.core import json_response_content
from acc.decorators import permission_required
from kiosks.views.slot import put_inventory_in_db


REVIEW_ALL_TYPE_ID = 1

@login_required
# @permission_required('kiosk_view', 'kiosk_global_inventory')
@permission_required('kiosk_view', 'kiosk_multi_settings')
def global_review_inventory(request):
    company = request.user.company

    if company:
        company_kiosks = request.db_session.query(Kiosk).\
            filter(Kiosk.company == company).all()
    else:
        raise Http404

    if request.method == "POST":
        request.db_session.autoflush = False
        data = loads(request.POST.get('data'))
        data_review = data['review']
        if data_review.has_key('kiosks'):
            kiosk_ids = data_review.get('kiosks', [])
            response = start_inventory(request, data_review, kiosk_ids if isinstance(kiosk_ids, list) else [kiosk_ids])
        elif data_review.has_key('kiosksStop'):
            kiosk_ids = data_review.get('kiosksStop', [])
            response = stop_inventory(request, kiosk_ids if isinstance(kiosk_ids, list) else [kiosk_ids])
        else:
            raise Http404
        return JsonResponse(response)
    elif request.method == "GET":
        kiosks_with_review = []
        kiosks_with_review_canceled = []
        kiosks_without_review = []
        for kiosk in company_kiosks:
            if kiosk.active_review_inventory is None:
                kiosks_without_review.append(kiosk)
            else:
                data_review = kiosk.active_review_inventory
                if data_review.dt_break and data_review.dt_end is None:
                    kiosks_with_review_canceled.append(kiosk)
                else:
                    kiosks_with_review.append(kiosk)
        response = json_response_content('success', 'Global Review')
        response['data'].update({
            'kiosks_without_review': kiosks_without_review,
            'kiosks_with_review': kiosks_with_review,
            'kiosks_with_review_canceled': kiosks_with_review_canceled,
        })
        return render(request, 'kiosk_global_review_inventory.html', response)
    else:
        return HttpResponseNotAllowed(('GET', 'POST'))


def start_inventory(request, data_review, kiosk_ids):
    load_db = data_review.get('loadDB', None)
    error_msg = 'Some errors occurred during updating kiosk settings'
    kiosks = request.db_session.query(Kiosk)\
        .filter(Kiosk.id.in_([int(kid) for kid in kiosk_ids])).all()

    if not kiosks:
        response = json_response_content('error', error_msg)
        response['errors'].append({'field': 'kiosks', 'message': "Select at leas one kiosk"})
        return JsonResponse(response)

    results = [put_inventory_in_db(request, kiosk, load_db=load_db) for kiosk in kiosks]

    succ_mess = 'Kiosk Global Review successfully started.'
    response = json_response_content('success', succ_mess, data=results)

    return response

def stop_inventory(request, kiosk_ids):
    kiosks = request.db_session.query(Kiosk).filter(Kiosk.id.in_([int(kid) for kid in kiosk_ids])).all()
    for kiosk in kiosks:
        review = kiosk.active_review_inventory
        review and review.kill()
    return json_response_content('success', 'Review was canceled!')