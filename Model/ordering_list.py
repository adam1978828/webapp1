# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'Denis Ivanets (denself@gmail.com)'


class OrderingList(Base):
    __tablename__ = 'k_ordering_list'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'), primary_key=True)
    type_id = sa.Column('type_id', sa.Numeric(2, 0), sa.ForeignKey('e_ordering_type.id'))
    algorithm = sa.Column('algorithm', sa.Text, default='')
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    kiosk = relationship('Kiosk')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
