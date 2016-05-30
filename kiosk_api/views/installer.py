# -*- coding: utf-8 -*-
import os
import datetime

from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from Model import Kiosk
from kiosk_api.utils import http_auth_require, get_kiosk_hostname, \
    get_recent_package


__author__ = 'Denis Ivanets (denself@gmail.com)'


def get_script(request):
    """Returns script content of file autorun.txt, which contains code
    that will be run before installation.
    :type request: WSGIRequest
    :return: Response
    :return: HttpResponse
    """
    path = os.path.join(settings.INSTALLER_DIR, 'autorun.txt')
    try:
        text = open(path).read()
        return HttpResponse(text)
    except IOError:
        return HttpResponseNotFound('NO FILE')


@require_POST
@csrf_exempt
@http_auth_require
def check_authorization(request):
    """Just checks if authorized user can use this coe to init kiosk
    >>> import requests
    >>> host = 'http://update.focusintense.com/kiosk_api/check_authorization/'
    >>> lo_host = 'http://localhost:8000/kiosk_api/check_authorization/'
    >>> auth = 'd.ivanets@kit-xxi.com.ua', '1234qwerASDF'
    >>> res = requests.post(host, data=dict(kioskid='ASDFZXCV'), auth=auth)
    :type request: WSGIRequest
    :return: Response
    :rtype: HttpResponse
    """
    code = request.POST.get('kioskid', '')
    try:
        kiosk = request.db_session.query(Kiosk) \
            .filter(Kiosk.company == request.user.company) \
            .filter(Kiosk.activation_code == code).one()
    except (NoResultFound, MultipleResultsFound):
        return HttpResponse('CODE_ERROR')
    else:
        now = datetime.datetime.utcnow()
        hostname = get_kiosk_hostname(kiosk)
        time_zone = kiosk.settings.timezone
        time_zone = time_zone.name if time_zone else "UTC"
        add_data = '{};{};{}'.format(hostname, kiosk.uuid, time_zone)
        if (now - kiosk.dt_sync).seconds <= 60:
            # return HttpResponse('UP;{};{}'.format(hostname, kiosk.uuid))
            return HttpResponse('UP;{}'.format(add_data))
        else:
            return HttpResponse('OK;{}'.format(add_data))


@http_auth_require
def get_package(request, test=False):
    """This view returns archive with KioskApplication.
     Requires http_base_auth authentication
    >>> import requests
    >>> host = 'http://66.6.127.167/kiosk_api/get_package/'
    >>> lo_host = 'http://localhost:8000/kiosk_api/get_package/'
    >>> auth = 'd.ivanets@kit-xxi.com.ua', '1234qwerASDF'
    >>> res = requests.get(host, auth=auth)
    >>> with open('package.tar.gz', 'wb') as f:
    ...     for chunk in res.iter_content():
    ...         f.write(chunk)
    """
    try:
        path, version = get_recent_package(test)
        wrapper = FileWrapper(file(path, "rb"))
    except IOError:
        return HttpResponseNotFound('NO FILE')
    else:
        response = HttpResponse(wrapper, content_type='application/x-gzip')
        response['Content-Disposition'] = 'attachment; filename=package.tar.gz'
        response['Content-Length'] = os.path.getsize(path)
        response['Package-Version'] = str(version)
        return response