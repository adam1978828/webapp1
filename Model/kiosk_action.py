# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'O.Tegelman'


class KioskAction(Base):
    __tablename__ = u'c_kiosk_action'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'))
    user_id = sa.Column('user_id', sa.String(36, 0), sa.ForeignKey('c_user.id'))
    action_id = sa.Column('action_id', sa.Numeric(2, 0), sa.ForeignKey('e_kiosk_action_type.id'))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    kiosk = relationship('Kiosk', uselist=False)
    user = relationship('User', uselist=False)
    action = relationship('KioskActionType', uselist=False)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()