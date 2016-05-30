# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


__author__ = 'D.Ivanets'


class Customer(Base):
    __tablename__ = u'c_customer'
    __table_args__ = {}
    id = sa.Column('id', sa.String(36), sa.ForeignKey('c_user.id'), primary_key=True)
    tariff_id = sa.Column('tariff_id', sa.Numeric, sa.ForeignKey('c_tariff_plan.id'))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship('User', backref='customer')
    tariff = relationship('TariffPlan', backref='customer')

    def __init__(self, user=None, tariff=None):
        self.user = user
        self.tariff = tariff

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
