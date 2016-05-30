# -*- coding: utf-8 -*-
from json import loads

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from Model import Kiosk, KioskBashCommand
from libs.validators.core import json_response_content
from WebApp.utils import alchemy_to_json

@login_required
def kiosk_bash(request, kiosk_id):
    kiosk = request.db_session.query(Kiosk).get(kiosk_id)
    if not kiosk:
        raise Http404

    commands = request.db_session.query(KioskBashCommand)\
        .filter(KioskBashCommand.kiosk == kiosk)\
        .order_by(KioskBashCommand.dt_create.desc())\
        .all()

    data = {
        'kiosk_id': int(kiosk_id),
        'commands': commands
    }
    return render(request, 'kiosk_bash.html', data)


@login_required
@require_POST
def ajax_kiosk_bash(request, kiosk_id):
    COMMAND_LIMIT = 20
    kiosk = request.db_session.query(Kiosk).get(kiosk_id)
    if not kiosk:
        return JsonResponse(json_response_content('error', 'Kiosk Not found'))

    command = KioskBashCommand()
    command.user = request.user
    command.kiosk = kiosk
    command.command = str(request.body)
    request.db_session.add(command)
    request.db_session.commit()

    to_delete = request.db_session.query(KioskBashCommand)\
        .filter(KioskBashCommand.kiosk_id == kiosk_id)\
        .order_by(KioskBashCommand.id.desc()).offset(COMMAND_LIMIT)\
        .all()
    [request.db_session.delete(command) for command in to_delete]
    request.db_session.commit()

    data = alchemy_to_json(command)
    data['user_id'] = request.user.email
    date = command.dt_create.strftime("%m.%d.%y %H:%M:%S")
    data['dt_create'] = date

    resp = json_response_content('success', 'Command saved for execution')
    resp['data'] = data

    return JsonResponse(resp)