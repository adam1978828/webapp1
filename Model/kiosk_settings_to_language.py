# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class KioskSettingsToLanguage(Base):
    __tablename__ = u'c_kiosk_settings_to_language'
    __table_args__ = {}
    kiosk_settings_id = sa.Column('kiosk_settings_id', sa.Numeric(10, 0),
                                  sa.ForeignKey('c_kiosk_settings.id'), primary_key=True)
    language_id = sa.Column('language_id', sa.Numeric(4, 0), sa.ForeignKey('e_language.id'), primary_key=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow)

    kiosk_settings = relationship('KioskSettings')
    kiosk = relationship('Kiosk', secondary='c_kiosk_settings', uselist=False)
    language = relationship('Language')

    sync_filter_rules = [lambda request: (KioskSettingsToLanguage.kiosk == request.kiosk), ]

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()