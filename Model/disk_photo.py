# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class DiskPhoto(Base):
    __tablename__ = 'c_disk_photo'
    __table_args__ = {}
    id = sa.Column('id', sa.String(32), primary_key=True)
    rfid = sa.Column('rfid', sa.String(12), sa.ForeignKey('disk.rf_id'))
    slot_id = sa.Column('slot_id', sa.Numeric(10, 0), sa.ForeignKey('k_slot.id'))
    dt_modify = sa.Column('dt_modify', sa.DateTime,
                          default=datetime.datetime.utcnow)

    disk = relationship('Disk', uselist=False)
    slot = relationship('Slot', uselist=False)

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()