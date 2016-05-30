# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ..base import Base

__author__ = 'O.Tegelman'


class KioskActionType(Base):
    __tablename__ = u'e_kiosk_action_type'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(2, 0), primary_key=True)
    alias = sa.Column('alias', sa.String(20))
    name = sa.Column('name', sa.String(40))

    def __init__(self, name=''):
        self.name = name

    def __repr__(self):
        return u"<%s(%s: '%s')>" % (self.__class__.__name__, self.id, self.name)

    def __unicode__(self):
        return self.__repr__()
