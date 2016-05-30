# -*- coding: utf-8 -*-
from json import loads

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from Model import Kiosk
from Model import VideoFile, VideoSchedule

from libs.validators.core import json_response_content, validation_error
from acc.decorators import permission_required
from django.core.exceptions import PermissionDenied
from sqlalchemy import or_, and_


@login_required
@permission_required('kiosk_trailers_schedule_view')
def trailers_schedule(request, kiosk_id):
    kiosk = request.db_session.query(Kiosk).filter_by(id=kiosk_id).first()
    company = kiosk.company

    company_trailers = request.db_session.query(VideoFile.id, VideoFile.alias)\
        .filter(or_(VideoFile.company_id == company.id, VideoFile.company_id == None)).all()
    trailers_dict = {int(vid): alias for vid, alias in company_trailers}

    if request.method == "POST":
        if 'kiosk_trailers_schedule_add' not in request.user.rights:
            raise PermissionDenied
        schedule = request.POST.get('schedule', None)
        response = json_response_content()

        if schedule:
            schedule = loads(schedule)
            not_yours = [v for v in schedule if int(v) not in trailers_dict.keys()]
            if not_yours:
                response['type'] = 'error'
                response['message'] = 'Some trailers are not yours'
                response['errors'].append(validation_error('schedule',
                                                           "You don't have trailers with ids %s" % ", ".join(not_yours)))
            else:
                response['type'] = 'success'
                response['message'] = 'Schedule was saved successfully'
                schedule = VideoSchedule(kiosk_id, "|".join(schedule))
                request.db_session.add(schedule)
                request.db_session.commit()
        return JsonResponse(response)
    elif request.method == "GET":
        script = request.db_session.query(VideoSchedule.script).filter(VideoSchedule.kiosk_id == kiosk.id) \
            .order_by(VideoSchedule.dt_modify.desc()).limit(1).scalar()
        
        schedule = [(id, trailers_dict[id]) for id in map(int, script.split('|'))] if script else []
        return render(request, 'kiosk_trailers_schedule.html',
                      {'kiosk_id': kiosk_id, 'company_trailers': company_trailers, 'schedule': schedule})
    else:
        raise Http404


@login_required
@require_POST
def ajax_disable(request, kiosk_id, state):
    kiosk = request.db_session.query(Kiosk).get(kiosk_id)
    if request.user.is_company and kiosk.company_id != request.user.company_id:
        return JsonResponse(json_response_content('error', 'Not allowed'))
    kiosk.is_running = bool(int(state))
    request.db_session.commit()
    return JsonResponse(json_response_content('success', ''))