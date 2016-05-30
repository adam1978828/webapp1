# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class VideoSchedule(Base):
    __tablename__ = 'v_video_schedule'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'))
    script = sa.Column('script', sa.Text, default='')
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    kiosk = relationship("Kiosk")

    sync_filter_rules = [lambda request: (VideoSchedule.kiosk == request.kiosk), ]

    def __init__(self, kiosk_id=None, script=None):
        if kiosk_id:
            self.kiosk_id = kiosk_id
        if script:
            self.script = script

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
