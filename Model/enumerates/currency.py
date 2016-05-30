# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ..base import Base

__author__ = 'D.Ivanets'


class Currency(Base):
    __tablename__ = u'e_currency'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(3, 0), primary_key=True)
    alias = sa.Column('alias', sa.String(128), default='')
    name = sa.Column('name', sa.String(4), default='')
    symbol = sa.Column('symbol', sa.String(64), default='')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.id, self.alias, )

    def __unicode__(self):
        return self.__repr__()
