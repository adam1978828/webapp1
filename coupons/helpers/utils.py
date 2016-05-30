# -*- coding: utf-8 -*-
__author__ = 'p.nevmerzhytskyi'

import inspect

import sqlalchemy as sa
from Model import base


def get_duplicate(old_obj, init_data=None):
    parents = inspect.getmro(type(old_obj))
    if not base.Base in parents:
        raise TypeError('The given parameter with type {} is not mapped by SQLAlchemy.'.format(type(old_obj)))
    mapper = sa.inspect(type(old_obj))
    if init_data:
        new_obj = type(old_obj)(**init_data)
    else:
        new_obj = type(old_obj)()

    for name, col in mapper.columns.items():
        # no PrimaryKey not Unique
        if not col.primary_key and not col.unique:
            setattr(new_obj, name, getattr(old_obj, name))

    return new_obj

def is_same_objects(first, second, fields):
    for field in fields:
        if getattr(first, field) != getattr(second, field):
            print getattr(first, field), getattr(second, field)
            return False
    return True

