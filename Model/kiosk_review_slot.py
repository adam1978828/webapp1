# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from base import Base
import utils

__author__ = 'O.Tegelman'


class KioskReviewSlot(Base):
    __tablename__ = u'c_kiosk_review_slot'
    __table_args__ = {}
    id = sa.Column('id', sa.String(36), primary_key=True, default=utils.unicode_uuid1)
    review_id = sa.Column('review_id', sa.String(36), sa.ForeignKey('c_kiosk_review.id'))
    slot_id = sa.Column('slot_id', sa.Numeric(10, 0), sa.ForeignKey('k_slot.id'))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    dt_check = sa.Column('dt_check', sa.DateTime)
    slot_state_before_id = sa.Column('slot_state_before_id', sa.Numeric(10, 0), sa.ForeignKey('e_slot_status.id'))
    slot_state_after_id = sa.Column('slot_state_after_id', sa.Numeric(10, 0), sa.ForeignKey('e_slot_status.id'))
    disk_before_id = sa.Column('disk_before_id', sa.String(18), sa.ForeignKey('disk.rf_id'))
    disk_after_id = sa.Column('disk_after_id', sa.String(18), sa.ForeignKey('disk.rf_id'))

    review = relationship('KioskReview', uselist=False)
    slot = relationship('Slot', uselist=False)
    kiosk = relationship("Kiosk", secondary='k_slot', uselist=False)

    sync_filter_rules = [
        lambda request: (KioskReviewSlot.kiosk == request.kiosk),
        lambda request: (KioskReviewSlot.dt_check == None),
    ]

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
