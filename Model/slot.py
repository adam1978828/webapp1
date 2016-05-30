# -*- coding: utf-8 -*-
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from base import Base


__author__ = 'D.Ivanets, D.Kalpakchi'


def onupdate_func(context):
    # kiosk_id = context.current_parameters['kiosk_id']
    return 1


class Slot(Base):
    __tablename__ = 'k_slot'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'))
    number = sa.Column('slot_number', sa.Numeric(3, 0))
    status_id = sa.Column('status_id', sa.Numeric(2, 0), sa.ForeignKey('e_slot_status.id'), onupdate=onupdate_func)
    is_to_check = sa.Column('is_to_check', sa.Boolean, default=False)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kiosk = relationship('Kiosk')
    status = relationship('SlotStatus')
    company = relationship('Company', secondary='c_kiosk', uselist=False)
    disk = relationship('Disk', uselist=False)
    photo = relationship('DiskPhoto', uselist=False, order_by='desc(DiskPhoto.dt_modify)')

    sync_filter_rules = [lambda request: (Slot.kiosk == request.kiosk), ]

    """
    def __init__(self, kiosk, number, status_id):
        self.kiosk = kiosk
        self.number = number
        self.status_id = status_id
        self.is_to_check = False
    """

    def __repr__(self):
        return u"<%s(%s:%s/%s)>" % (self.__class__.__name__, self.id, self.kiosk_id, self.number)

    def __unicode__(self):
        return self.__repr__()
