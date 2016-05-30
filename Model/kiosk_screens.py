# -*- coding: utf-8 -*-
import uuid
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from base import Base

__author__ = 'D.Kalpakchi'


class KioskScreens(Base):
    __tablename__ = u'c_kiosk_screens'
    __table_args__ = {}
    id = sa.Column('id', sa.String(32), primary_key=True)
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'))
    done = sa.Column('done', sa.Boolean, default=False)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow)

    kiosk = relationship('Kiosk', uselist=False)

    sync_filter_rules = [lambda request: (KioskScreens.kiosk == request.kiosk), ]

    def __init__(self, kiosk_id=None):
        self.id = str(uuid.uuid1().hex)
        if kiosk_id:
            self.kiosk_id = kiosk_id

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @hybrid_property
    def close_to_now(self):
        delta = datetime.datetime.utcnow() - self.dt_modify
        return delta.total_seconds() < 300