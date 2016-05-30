# -*- coding: utf-8 -*-
import base64
import json
import os
import datetime
from django.conf import settings

from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Model import KioskScreens
from WebApp.utils import z_alchemy_from_json
import kiosk_api.utils


__author__ = 'D.Ivanets'

BOT_TOP_PATHS = {u'bot': settings.SCREEN_BOT_DIR, u'top': settings.SCREEN_TOP_DIR}

@require_POST
@csrf_exempt
def upload_screenshot(request):
    """After kiosk make screenshots, It uploads them here
    :param request:
    :return:
    """
    # Check, if there is a kiosk.
    # TODO: make is a decorator
    if not request.kiosk:
        return HttpResponseForbidden()

    files_in = None
    if request.META.get(u'CONTENT_TYPE') == u'application/json':
        data_in = json.loads(request.body)
    else:
        files_in = request.FILES
        data_in = request.POST
    data_out = {'success': True}
    #for compatibility with old kiosk versions (<=0.0.46)
    # decode pictures and save them.
    # This is not a really good way to upload images, just legacy code.
    # get files from request
    if files_in is None:
        for pic, path in [('data_bot', settings.SCREEN_BOT_DIR),
                          ('data_top', settings.SCREEN_TOP_DIR)]:
            data = data_in.pop(pic, None)
            img_path = os.path.join(path, '{}.jpg'.format(data_in['id']))
            if data:
                kiosk_api.utils.__old_save_img(data, img_path)
    # for kiosks with version more than 0.0.46
    else:
        screens = {}
        for key, path in BOT_TOP_PATHS.iteritems():
            images = request.FILES.getlist(key, [])
            image = images[0] if images else None
            screens[path] = image
        kiosk_api.utils.save_screenshots(screens)

    # Save information about screenshots into db.
    z_alchemy_from_json(alchemy_type=KioskScreens,
                        json_obj=data_in,
                        session=request.db_session,
                        cur_time=datetime.datetime.utcnow())

    return JsonResponse(data_out)