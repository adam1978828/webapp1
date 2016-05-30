# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa

from sqlalchemy.orm import relationship
from .base import Base

__author__ = 'O.Tegelman'


class CouponView(Base):
    __tablename__ = u'coupons_view'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric, primary_key=True)
    company_id = sa.Column('company_id', sa.Numeric(10, 0))
    company_name = sa.Column('company_name', sa.String(255))
    coupon_type = sa.Column('coupon_type', sa.String(100))
    coupon_pattern = sa.Column('coupon_pattern', sa.String(20))
    coupon_code = sa.Column('coupon_code', sa.String(20))
    usage_amount = sa.Column('usage_amount', sa.Numeric)
    per_card_usage = sa.Column('per_card_usage', sa.Numeric(10, 0))
    used_total = sa.Column('used_total', sa.Numeric(10, 0))
    dt_start = sa.Column('dt_start', sa.DateTime)
    dt_end = sa.Column('dt_end', sa.DateTime)
    is_deleted = sa.Column('is_deleted', sa.Boolean)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()