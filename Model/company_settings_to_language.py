# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


__author__ = 'D.Ivanets'


class CompanySettingsToLanguage(Base):
    __tablename__ = u'c_company_settings_to_language'
    __table_args__ = {}
    company_settings_id = sa.Column('company_settings_id', sa.Numeric(10, 0),
                                    sa.ForeignKey('c_company_settings.id'), primary_key=True)
    language_id = sa.Column('language_id', sa.Numeric(4, 0), sa.ForeignKey('e_language.id'), primary_key=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow)

    company_settings = relationship('CompanySettings')
    language = relationship('Language')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
