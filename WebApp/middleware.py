# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from sqlalchemy.orm.exc import NoResultFound

from Model import User, AnonymousUser, ServerData, Kiosk, Company
from Model.company_site import CompanySite


__author__ = 'D.Ivanets, D.Kalpakchi'

SESSION_KEY = '_auth_user_id'
SET_POSTGRE_AUDIT_SESSION_VARIABLES = 'SET "web.kiosk" TO %s; SET "web.user" TO %s;' \
                                      'SET "web.ip_address" TO %s; SET "web.browser" TO %s;' \
                                      'SET "web.original_url" TO %s; SET "web.named_url" TO %s;' \
                                      'SET "web.request_type" TO %s; SET "web.is_ajax" TO %s'

SET_POSTGRE_AUDIT_SESSION_VARIABLE = 'SET "web.{0}" TO :{1}'


class SQLAlchemySessionMiddleware(object):
    def process_request(self, request):
        request.db_session = settings.SESSION()

    def process_response(self, request, response):
        try:
            session = request.db_session
        except AttributeError:
            return response
        try:
            session.commit()
            return response
        finally:
            session.rollback()

    def process_exception(self, request, exception):
        try:
            session = request.db_session
        except AttributeError:
            return
        session.rollback()


def get_user(request):
    if SESSION_KEY in request.session:
        try:
            if request.company:
                return request.db_session.query(User).filter_by(user_type_id=1)\
                    .filter_by(id=request.session[SESSION_KEY]).one()
            else:
                return request.db_session.query(User).filter(User.user_type_id.in_([2, 3]))\
                    .filter_by(id=request.session[SESSION_KEY]).one()
        except:
            return AnonymousUser()
        # return request.db_session.query(User).filter_by(id=request.session[SESSION_KEY]).one()
    else:
        return AnonymousUser()


class SQLAlchemyAuthMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), \
            "The SQLAlchemy authentication middleware requires session middleware to be installed. Edit your " \
            "MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        request.user = SimpleLazyObject(lambda: get_user(request))
        request.user.rights = request.user.rights_func()


class ServerStateMiddleware(object):
    def process_request(self, request):
        request.server_state = request.db_session.query(ServerData).one()


class KioskApiMiddleware(object):
    def process_request(self, request):
        request.cur_datetime = datetime.datetime.utcnow()
        if request.path.startswith(u'/kiosk_api/'):
            request.kiosk = None
            if 'kiosk_uuid' in request.COOKIES:
                try:
                    request.kiosk = request.db_session.query(Kiosk)\
                        .filter_by(uuid=request.COOKIES['kiosk_uuid']).one()
                except NoResultFound:
                    pass


class SiteMiddleware(object):
    FORWARDED_FOR_FIELDS = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_FORWARDED_HOST',
        'HTTP_X_FORWARDED_SERVER',
    ]

    def process_request(self, request):
        for field in self.FORWARDED_FOR_FIELDS:
            if field in request.META:
                if ',' in request.META[field]:
                    parts = request.META[field].split(',')
                    request.META[field] = parts[-1].strip()
        request.company = request.db_session.query(Company).join(CompanySite) \
            .filter_by(domain=request.get_host().lower()).first()
        if request.company:
            request.urlconf = 'sites.urls'
            print request.get_host(), request.company

import pytz

from django.utils import timezone


class TimezoneMiddleware(object):
    def process_request(self, request):
        tzname = request.user.local_tz
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()


class PostgreAuditMiddleware(object):
    def process_request(self, request, *args, **kwargs):
        cursor = request.db_session
        kiosk = getattr(request, 'kiosk', None)

        data = dict()

        data['kiosk'] = kiosk.id if kiosk else None
        data['user'] = request.user.id
        data['ip_address'] = request.environ.get('HTTP_X_REAL_IP') if 'HTTP_X_REAL_IP' in request.environ else request.environ.get('REMOTE_ADDR') if 'REMOTE_ADDR' in request.environ else None
        data['browser'] = request.META.get('HTTP_USER_AGENT')
        data['original_url'] = request.build_absolute_uri()
        data['named_url'] = None
        data['request_type'] = request.method
        data['is_ajax'] = 1 if request.is_ajax() else 0

        variables = []

        for k, v in data.iteritems():
            if v:
                variables.append(SET_POSTGRE_AUDIT_SESSION_VARIABLE.format(k, k))

        set_session_vars_sql = ';'.join(variables)
        if set_session_vars_sql:
            cursor.execute(set_session_vars_sql, data)