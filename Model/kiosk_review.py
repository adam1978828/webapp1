# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session

from base import Base
from kiosk_review_slot import KioskReviewSlot
import utils

__author__ = 'O.Tegelman'


class KioskReview(Base):
    __tablename__ = u'c_kiosk_review'
    __table_args__ = {}
    id = sa.Column('id', sa.String(36), primary_key=True, default=utils.unicode_uuid1)
    # id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'))
    user_id = sa.Column('user_id', sa.String(36, 0), sa.ForeignKey('c_user.id'))
    type_id = sa.Column('type_id', sa.Numeric(2, 0), sa.ForeignKey('e_kiosk_review_type.id'))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    load_db = sa.Column('load_db', sa.Boolean)

    dt_start = sa.Column('dt_start', sa.DateTime, default=None)
    dt_end = sa.Column('dt_end', sa.DateTime, default=None)
    dt_break = sa.Column('dt_break', sa.DateTime, default=None)
    # last_slot_id = sa.Column('last_slot_id', sa.Numeric(10, 0), sa.ForeignKey('k_slot.id'))
    # slot_reviewed_count = sa.Column('slot_reviewed_count', sa.Numeric(4, 0))

    kiosk = relationship('Kiosk', uselist=False)
    user = relationship('User', uselist=False)
    type = relationship('KioskReviewType', uselist=False)
    # last_slot = relationship('Slot', uselist=False)
    review_slots = relationship('KioskReviewSlot', lazy='dynamic', order_by="KioskReviewSlot.slot_id")

    sync_filter_rules = [
        lambda request: (KioskReview.kiosk == request.kiosk),
        # lambda request: (KioskReview.dt_start == None),
    ]

    @property
    def checked_total(self):
        return self.review_slots\
            .filter(KioskReviewSlot.dt_check != None)\
            .count()

    @property
    def last_slot(self):
        return self.review_slots\
            .filter(KioskReviewSlot.dt_check != None)\
            .order_by(KioskReviewSlot.dt_check.desc()).first()

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    def kill(self):
        self.dt_break = datetime.datetime.utcnow()
        object_session(self).add(self)
        object_session(self).commit()