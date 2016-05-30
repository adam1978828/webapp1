__author__ = 'D.Kalpakchi'

from libs.utils.string_functions import convert2camelCase


def convert_json_keys_to_camelcase(d):
    return {convert2camelCase(k): convert_json_keys_to_camelcase(v)
            if isinstance(v, dict) else v for k, v in d.iteritems()}


def merge_objects(d1, d2):
    d1.update(d2)
    return d1