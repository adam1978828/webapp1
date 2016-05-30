# -*- coding: utf-8 -*-
__author__ = 'D.Ivanets'


def tz_to_tz(dt, from_tz, to_tz):
    import pytz
    from dateutil import parser
    if isinstance(dt, str) or isinstance(dt, unicode):
        dt = parser.parse(dt)
    from_tz = pytz.timezone(from_tz)
    to_tz = pytz.timezone(to_tz)
    return from_tz.localize(dt).astimezone(to_tz).replace(tzinfo=None)


def to_utc(dt, timezone):
    return tz_to_tz(dt, timezone, 'UTC')


def from_utc(dt, timezone):
    return tz_to_tz(dt, 'UTC', timezone)