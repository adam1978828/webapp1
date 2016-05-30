# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

__author__ = 'D.Kalpakchi'

Base = declarative_base()
Base.sync_filter_rules = []
Base.load_filter_rules = []


class ExtMixin(object):
    """
    Mixin that adds extra functionality to SQLAlchemy Base class.
    In particular:
        => errors list for models
    """

    __mapper_args__ = {'always_refresh': True}

    def __init__(self):
        self.__errors = list()

    def no_errors(self):
        return not self.__errors

    @hybrid_property
    def errors(self):
        return self.__errors

    @classmethod
    def copy(cls, obj):
        # maybe we also need to exclude some relationships here
        # definitely add some try/except
        # so it's just a fresh version for now!
        from sqlalchemy import inspect
        instance = cls()
        mapper = inspect(cls)
        primary_key = mapper.primary_key[0]
        for column in mapper.attrs:
            if hasattr(column, 'expression') and column.expression != primary_key:
                instance.__setattr__(column.key, obj.__getattribute__(column.key))
        return instance