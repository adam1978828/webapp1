# -*- coding: utf-8 -*-
__author__ = 'p.nevmerzhytskyi'

import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates, object_session


from .base import Base
from deal import Deal

class CouponUsageInfo(Base):
    """
    CouponUsageInfo class
    params:
    """
    __tablename__ = u'c_coupon_usage_info'
    __table_args__ = {}

    coupon_id = sa.Column('coupon_id', sa.Numeric, sa.ForeignKey('d_coupon.id'), primary_key=True)
    card_id = sa.Column('card_id', sa.String(32), sa.ForeignKey('c_card.id'), primary_key=True)
    usage_amount = sa.Column('usage_amount', sa.Numeric(10, 0), default=0)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    coupon = relationship('Coupon')
    card = relationship('Card')
    company = relationship('Company', secondary='d_coupon', uselist=False)

    sync_filter_rules = [lambda request: (CouponUsageInfo.company == request.kiosk.company), ]

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, unicode(self.coupon_id)+' '+unicode(self.card_id))

    def __unicode__(self):
        return self.__repr__()

    def refresh_usage_amount(self):
        accepted_status_list = (
            201, 301, 311, 511, 601, 521, 621, 701, 321, 231, 241)
        if object_session(self):
            value = object_session(self).query(Deal)\
                .filter(Deal.coupon == self.coupon)\
                .filter(Deal.card == self.card)\
                .filter(Deal.deal_status_id.in_(accepted_status_list))\
                .count()
        else:
            value = 0
        self.usage_amount = value

    @property
    def actual_usage_amount(self):
        self.refresh_usage_amount()
        return self.usage_amount