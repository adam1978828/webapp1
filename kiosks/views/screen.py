# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from Model import KioskScreens
from libs.validators.core import json_response_content
from acc.decorators import permission_required


@login_required
@permission_required('kiosk_view')
def screens(request, kiosk_id):
    kiosk_screens = request.db_session.query(KioskScreens).filter_by(kiosk_id=kiosk_id).filter_by(done=True)\
        .order_by(KioskScreens.dt_modify.desc())
    return render(request, 'kiosk_screens.html', {
        'kiosk_id': int(kiosk_id),
        'kiosk_screens': kiosk_screens.limit(10), 
        'latest': kiosk_screens.first()
    })


@login_required
@require_POST
def make_screen(request, kiosk_id):
    import os
    from django.conf import settings
    screen_request = KioskScreens(int(kiosk_id))
    request.db_session.add(screen_request)
    request.db_session.commit()
    top_path = os.path.join(settings.SCREEN_TOP_DIR, '%s.jpg' % screen_request.id)
    bottom_path = os.path.join(settings.SCREEN_BOT_DIR, '%s.jpg' % screen_request.id)
    while True:
        if os.path.exists(top_path) and os.path.exists(bottom_path):
            response = json_response_content('success', 'Screen was successfully requested')
            response['data']['topScreen'] = '%s%s.jpg' % (settings.SCREEN_TOP_URL, screen_request.id)
            response['data']['bottomScreen'] = '%s%s.jpg' % (settings.SCREEN_BOT_URL, screen_request.id)
            return JsonResponse(response)