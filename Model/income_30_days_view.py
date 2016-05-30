# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base


__author__ = 'D.Ivanets, D.Kalpakchi'


class Income30DaysView(Base):
    __tablename__ = u'income_30_days_view'
    __table_args__ = {}
    company_id = sa.Column('company_id', sa.Numeric(10))
    income_date = sa.Column('income_date', sa.DateTime, primary_key=True)
    rental_income = sa.Column('rental_income', sa.Numeric(10))
    sale_income = sa.Column('sale_income', sa.Numeric(10))
    total_income = sa.Column('total_income', sa.Numeric(10))

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.income_date,)

    def __unicode__(self):
        return self.__repr__()