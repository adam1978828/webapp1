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
from Model.kiosk_bash_command import KioskBashCommand
from WebApp.utils import z_alchemy_from_json


__author__ = 'D.Ivanets'


@require_POST
@csrf_exempt
def bash_result(request):
    if not request.kiosk:
        return HttpResponseForbidden()
    data_in = json.loads(request.body)
    data_out = {'success': True}

    command = request.db_session.query(KioskBashCommand).get(data_in['id'])
    if command:
        command.exec_result = data_in.get('exec_result')
        command.exec_err = data_in.get('exec_err')
        request.db_session.commit()

    return JsonResponse(data_out)