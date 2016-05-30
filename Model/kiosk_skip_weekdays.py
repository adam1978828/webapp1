# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class KioskSkipWeekdays(Base):
    __tablename__ = u'c_kiosk_skip_weekdays'
    __table_args__ = {}
    kiosk_settings_id = sa.Column('kiosk_settings_id', sa.Numeric(10, 0),
                                  sa.ForeignKey('c_kiosk_settings.id'), primary_key=True)
    weekday = sa.Column('weekday', sa.Numeric(1, 0), primary_key=True)
    is_active = sa.Column('is_active', sa.Boolean, default=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    kiosk_settings = relationship('KioskSettings')
    kiosk = relationship('Kiosk', secondary='c_kiosk_settings', uselist=False)

    sync_filter_rules = [lambda request: (KioskSkipWeekdays.kiosk_settings_id == request.kiosk.id), ]
    load_filter_rules = [lambda request: (KioskSkipWeekdays.is_active == True), ]

    def __init__(self, kiosk_settings, day=None):
        if kiosk_settings:
            self.kiosk_settings_id = kiosk_settings.id
        if day: 
            self.weekday = day

    def __repr__(self):
        return u"<%s(%s:%s)>" % \
               (self.__class__.__name__, self.kiosk_settings_id, self.weekday)

    def __unicode__(self):
        return self.__repr__()
