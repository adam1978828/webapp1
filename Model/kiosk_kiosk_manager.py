# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class KioskKioskManager(Base):
    __tablename__ = 'c_kiosk_kiosk_manager'
    __table_args__ = {}
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'), primary_key=True)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'), primary_key=True)

    user = relationship('User')
    kiosk = relationship('Kiosk')

    def __init__(self, kiosk_id, user_id):
        self.kiosk_id = kiosk_id
        self.user_id = user_id

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.kiosk_id, self.user_id)

    def __unicode__(self):
        return self.__repr__()
