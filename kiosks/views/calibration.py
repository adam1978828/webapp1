# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from Model import Kiosk, KioskCalibration
from libs.validators.core import json_response_content


@login_required
def kiosk_calibration(request, kiosk_id):
    kiosk = request.db_session.query(Kiosk).get(kiosk_id)
    if not kiosk:
        raise Http404
    data = {
        'kiosk_id': int(kiosk_id),
        'calibration': request.db_session.query(KioskCalibration).filter_by(id = kiosk_id).first()
    }
    return render(request, 'kiosk_calibration.html', data)


@login_required
@require_POST
def ajax_kiosk_calibration(request, kiosk_id):
    kiosk = request.db_session.query(Kiosk).get(kiosk_id)
    if not kiosk:
        return JsonResponse(json_response_content('error', 'Kiosk Not found'))
    calibration = request.db_session.query(KioskCalibration).filter_by(id = kiosk_id).first()
    if not calibration:
        calibration = KioskCalibration()
        calibration.id = kiosk_id
    calibration.top_offset = request.POST.get('topOffset', None)
    calibration.bottom_offset = request.POST.get('bottomOffset', None)
    calibration.exchange_offset = request.POST.get('exchangeOffset', None)
    calibration.back_offset = request.POST.get('backOffset', None)
    calibration.pulses_per_slot = request.POST.get('pulsesPerSlot', None)
    calibration.distance1 = request.POST.get('distance1', None)
    calibration.distance2 = request.POST.get('distance2', None)
    calibration.retry = request.POST.get('retry', None)
    calibration.offset2xx = request.POST.get('offset2xx', None)
    calibration.offset6xx = request.POST.get('offset6xx', None)
    response = json_response_content('success', 'You are changing kiosk calibration settings.')
    if calibration.no_errors():
        request.db_session.add(calibration)
        request.db_session.commit()
    else:
        request.db_session.rollback()
        response = json_response_content('error', 'Something went wrong during kiosk calibration changing.')
        for error in calibration.errors:
            response['errors'].append(error)
    return JsonResponse(response)
