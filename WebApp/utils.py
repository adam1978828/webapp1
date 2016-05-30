# -*- coding: utf-8 -*-
import json
import os
import traceback, sys, pprint

from dateutil import parser
from django.conf import settings
from django.core.mail import send_mail

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.exc import NoResultFound

from Model.encoder import AlchemyEncoder

__author__ = u'D.Ivanets'


def random_string(length):
    import random
    import string

    return u''.join(random.choice(string.ascii_letters + string.digits)
                    for _ in range(length))


def save_file(new_file, path):
    """
    Little helper to save a file
    """

    full_file_path = os.path.join(settings.MEDIA_ROOT, unicode(path))
    parent_dirs = os.path.dirname(full_file_path)
    if not os.path.exists(parent_dirs):
        os.makedirs(parent_dirs)
    fd = open(full_file_path, u'wb')
    for chunk in new_file.chunks():
        fd.write(chunk)
    fd.close()


def open_file(path):
    try:
        fd = open(u'%s/%s' % (settings.MEDIA_ROOT, str(path)), u'rb')
        s = fd.read()
        fd.close()
        return s
    except IOError:
        return u''


def save_transaction(t_object, t_result):
    t_object.amount = float(t_result.get(u'amount', 0))
    t_object.authorization_number = t_result.get(u'authorization_num', u'')
    t_object.bank_message = t_result.get(u'bank_message', u'')
    t_object.bank_resp_code = t_result.get(u'bank_resp_code', u'')
    t_object.client_ip = t_result.get(u'client_ip', u'')
    t_object.exact_message = t_result.get(u'exact_message', u'')
    t_object.exact_resp_code = t_result.get(u'exact_resp_code', u'')
    t_object.gateway_id = t_result.get(u'gateway_id', u'')
    t_object.partial_redemption = bool(t_result.get(u'exact_message', 0))
    t_object.retrieval_ref_no = t_result.get(u'retrieval_ref_no', u'')
    t_object.sequence_no = t_result.get(u'sequence_no', u'')
    t_object.transaction_approved = bool(t_result.get(u'transaction_approved', 1))
    t_object.transaction_error = bool(t_result.get(u'transaction_error', 0))
    t_object.transaction_tag = int(t_result.get(u'transaction_tag', 0)) \
        if t_result.get(u'transaction_tag', 0) else None
    t_object.transaction_type = t_result.get(u'transaction_type', u'')
    t_object.transarmor_token = t_result.get(u'transarmor_token', u'')

    return t_object


def alchemy_to_json(obj):
    """
    Converts SQLAlchemy objects to serial
    :return:
    """
    return json.loads(json.dumps(obj, cls=AlchemyEncoder))


def alchemy_list_to_json(obj):
    """
    Converts SQLAlchemy objects to serial
    :return:
    """
    return {type(obj[0]).__tablename__: alchemy_to_json(obj)} if obj else {}


def alchemy_from_json(alchemy_type, json_obj, cur_time=None):
    """

    :param alchemy_type: SQLAlchemy class object
    :type alchemy_type: sqlalchemy.ext.declarative.api.DeclarativeMeta
    :param json_obj: JSON object
    :type json_obj: dict
    :return: SQLAlchemy object, with fields, mapped from JSON
    """
    if isinstance(json_obj, list):
        return [alchemy_from_json(alchemy_type, item, cur_time)
                for item in json_obj]
    if isinstance(alchemy_type, DeclarativeMeta):
        alchemy_object = alchemy_type()
    else:
        alchemy_object = alchemy_type
    for key, value in json_obj.items():
        if key.startswith(u'dt_'):
            alchemy_object.__setattr__(key, parser.parse(value) if value is not None else value)
        elif key.startswith(u't_'):
            alchemy_object.__setattr__(key, parser.parse(value).time() if value is not None else value)
        else:
            alchemy_object.__setattr__(key, value)
    if cur_time:
        try:
            alchemy_object.__getattribute__(u'dt_modify')
            alchemy_object.__setattr__(u'dt_modify', cur_time)
        except AttributeError:
            pass
    return alchemy_object


def z_alchemy_from_json(alchemy_type, json_obj, session, cur_time=None):
    if isinstance(json_obj, list):
        return [z_alchemy_from_json(alchemy_type, item, session, cur_time) for item in json_obj]
    alchemy_object = session.query(alchemy_type)
    for column in alchemy_type.__mapper__.primary_key:
        alchemy_object = alchemy_object.filter_by(**{column.name: json_obj[column.name]})
    try:
        alchemy_object = alchemy_object.one()
    except NoResultFound:
        alchemy_object = alchemy_type()

    for key, value in json_obj.items():
        if key.startswith(u'dt_'):
            alchemy_object.__setattr__(key, parser.parse(value) if value is not None else value)
        elif key.startswith(u't_'):
            alchemy_object.__setattr__(key, parser.parse(value).time() if value is not None else value)
        else:
            alchemy_object.__setattr__(key, value)

    if cur_time:
        if hasattr(alchemy_object, 'dt_modify'):
            alchemy_object.dt_modify = cur_time
    session.add(alchemy_object)
    return alchemy_object


def splitext(path):
    """Split the extension from a pathname.
    Extends default os.path.splitext function,
    handling files with double extension

    Extension is everything from the last dot to the end, ignoring
    leading dots.
    :type path: unicode
    :return: (root, ext)
    """
    for ext in ['.tar.gz', '.tar.bz', '.tar.bz2', '.tar.xz',
                '.tar.7z', '.tar.lz', '.tar.z', '.tar.lzma']:
        if path.lower().endswith(ext):
            return path[:-len(ext)], path[-len(ext):]
    return os.path.splitext(path)


def get_traceback_with_locals():
    formatted_lines = traceback.format_exc().splitlines()
    exc_info = sys.exc_info()[2]
    yield formatted_lines.pop(0)

    while exc_info:
        yield '='*8 + formatted_lines.pop(0)
        yield '='*8 + formatted_lines.pop(0)
        local = pprint.pformat({key: value for key, value in
                                exc_info.tb_frame.f_locals.items()
                                if not key.startswith('__')})
        local = ' '+local[1:-1]
        for line in local.splitlines(): yield '='*0 + line
        exc_info = exc_info.tb_next

    yield formatted_lines.pop(0)


def get_traceback():
    return '\n'.join(get_traceback_with_locals())


def send_to_admin(subject, message):
    """
    >>> e = Exception()
    >>> send_to_admin(e, get_traceback())
    :param subject: error (for example)
    :param message: error trace back (for example)
    :return:
    """
    admin_mails = [mail for name, mail in settings.ADMINS]
    send_mail(subject, message, settings.SERVER_EMAIL, admin_mails, fail_silently=True)
