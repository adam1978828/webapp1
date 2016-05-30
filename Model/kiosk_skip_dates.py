# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
from base import Base
import datetime

__author__ = 'D.Ivanets'


class KioskSkipDates(Base):
    __tablename__ = u'c_kiosk_skip_dates'
    __table_args__ = {}
    kiosk_settings_id = sa.Column('kiosk_settings_id', sa.Numeric(10, 0),
                                  sa.ForeignKey('c_kiosk_settings.id'), primary_key=True)
    day = sa.Column('day', sa.Numeric(2, 0), primary_key=True)
    month = sa.Column('month', sa.Numeric(2, 0), primary_key=True)
    year = sa.Column('year', sa.Numeric(4, 0), primary_key=True)
    is_active = sa.Column('is_active', sa.Boolean, default=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    kiosk_settings = relationship('KioskSettings')
    kiosk = relationship('Kiosk', secondary='c_kiosk_settings', uselist=False)

    sync_filter_rules = [lambda request: (KioskSkipDates.kiosk_settings_id == request.kiosk.id), ]
    load_filter_rules = [lambda request: (KioskSkipDates.is_active == True), ]

    def __init__(self, kiosk_settings, date=None):
        if kiosk_settings:
            self.kiosk_settings_id = kiosk_settings.id
        if date:
            self.day = date[0]
            self.month = date[1]
            self.year = date[2]

    def __repr__(self):
        return u"<%s(%s:%s/%s/%s)>" % \
               (self.__class__.__name__, self.kiosk_settings_id, self.day, self.month, self.year,)

    def __unicode__(self):
        return self.__repr__()

    def date(self, year=None):
        """Convert skip date to datetime
        :params year: optional param for "Yearly skipped dates" support
        """
        return datetime.date(year if year else self.year, self.month, self.day)
