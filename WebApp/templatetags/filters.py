import datetime
import pickle

from dateutil.parser import parse

from django import template

register = template.Library()


@register.filter(name='get_dict_val')
def get_item(dictionary, key):
    """
    Function is used to get dict val by the key

    Args:
        dictionary (dict): input dictionary
        key (any type): key of the dictionary

    Returns:
        val: dictionary value bu the key, None if no matches found
    """
    return dictionary.get(key)


@register.filter(name='get_dict_item_from_list')
def get_item(list_of_dict, key):
    for val in list_of_dict:
        if key in val:
            return val[key]

    return None


@register.filter
def month_name(month_number):
    """ returns month_name by month_number """
    import calendar

    return calendar.month_name[int(month_number)]


@register.filter
def localize(dt, timezone):
    """
    Localizes time to given timezone.
    :param dt: str, time to localize, either datetime.datetime or string in
        format "%H:%M"
    :param timezone: the name of the timezone
    """
    import pytz

    if dt and timezone:
        utc = pytz.timezone('UTC')
        local = pytz.timezone(timezone)
        return utc.localize(parse(dt)).astimezone(local).time()


@register.filter
def to_milliseconds(dt):
    """
    Converts time to seconds
    :param dt:
    :return:
    """
    import time
    return int(time.mktime(dt.timetuple())*1000)


@register.filter
def normalize_timezone(timezone_name):
    if isinstance(timezone_name, basestring):
        timezone_name = timezone_name.replace('/', ' / ')
        timezone_name = timezone_name.replace('_', ' ')
    return timezone_name


@register.filter
def timezone_to_offset(timezone_name):
    import pytz

    tz = pytz.timezone(timezone_name)
    dt = datetime.datetime.now(tz)
    return -int(dt.utcoffset().total_seconds() / 60)


@register.filter
def available_formats(movie, company):
    return movie.available_disk_formats(company.id) if company else []


@register.filter
def available_kiosk_formats(movie, kiosk):
    return movie.disk_formats_in_kiosk(kiosk.id) if kiosk else []


@register.filter
def get_upc(movie, format_id):
    return movie.upc_matching(format_id)


@register.filter
def intersect(lst1, lst2):
    return set(lst1) & set(lst2) if lst2 and lst1 else False


@register.filter
def day_diff(date, days):
    if isinstance(date, datetime.datetime):
        return date - datetime.timedelta(days=days)
    else:
        try:
            return parse(date) - datetime.timedelta(days=days)
        except:
            return None


@register.filter
def subtract(minuend, subtrahend):
    return minuend - subtrahend


@register.filter
def proc_params(params, coupon_type_id):
    params = pickle.loads(params)
    result = params if type(params) in [list, tuple] else [params]
    if coupon_type_id == 4:
        result[0] = result[0] - result[1]
    return result