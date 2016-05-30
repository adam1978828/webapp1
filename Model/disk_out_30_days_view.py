# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base


__author__ = 'D.Ivanets, D.Kalpakchi'


class DiskOut30DaysView(Base):
    __tablename__ = u'disk_out_30_days_view'
    __table_args__ = {}

    company_id = sa.Column('company_id', sa.Numeric(10))
    deal_dt = sa.Column('deal_dt', sa.DateTime, primary_key=True)
    disk_out_count = sa.Column('disk_out_count', sa.Numeric(10))

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.deal_dt,)

    def __unicode__(self):
        return self.__repr__()