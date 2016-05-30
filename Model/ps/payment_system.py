# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from ..base import Base

__author__ = 'D.Ivanets'


class PaymentSystem(Base):
    __tablename__ = u'ps_payment_system'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(3, 0), primary_key=True)
    name = sa.Column('name', sa.String(32), default='')
    alias = sa.Column('alias', sa.String(32), default='')
    description = sa.Column('description', sa.String(256), default='')
    url = sa.Column('url', sa.String(128), default='')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.id, self.name,)

    def __unicode__(self):
        return self.__repr__()
