# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


__author__ = 'D.Ivanets, D.Kalpakchi'


class CompanySkipDates(Base):
    __tablename__ = u'c_company_skip_dates'
    __table_args__ = {}
    company_settings_id = sa.Column('company_settings_id', sa.Numeric(10, 0),
                                    sa.ForeignKey('c_company_settings.id'), primary_key=True)
    day = sa.Column('day', sa.Numeric(2, 0), primary_key=True)
    month = sa.Column('month', sa.Numeric(2, 0), primary_key=True)
    year = sa.Column('year', sa.Numeric(4, 0), primary_key=True)

    company_settings = relationship('CompanySettings')

    def __init__(self, company_settings, date=None):
        if company_settings:
            self.company_settings_id = company_settings.id
        if date:
            self.day = date[0]
            self.month = date[1]
            self.year = date[2]

    def __repr__(self):
        return u"<%s(%s:%s/%s/%s)>" % \
               (self.__class__.__name__, self.company_settings_id, self.day, self.month, self.year,)

    def __unicode__(self):
        return self.__repr__()
