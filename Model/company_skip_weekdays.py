# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


__author__ = 'D.Ivanets, D.Kalpakchi'


class CompanySkipWeekdays(Base):
    __tablename__ = u'c_company_skip_weekdays'
    __table_args__ = {}
    company_settings_id = sa.Column('company_settings_id', sa.Numeric(10, 0),
                                    sa.ForeignKey('c_company_settings.id'), primary_key=True)
    weekday = sa.Column('weekday', sa.Numeric(1, 0), primary_key=True)

    company_settings = relationship('CompanySettings')

    def __init__(self, company_settings, day=None):
        if company_settings:
            self.company_settings_id = company_settings.id
        if day:
            self.weekday = day

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.company_settings_id, self.weekday,)

    def __unicode__(self):
        return self.__repr__()
