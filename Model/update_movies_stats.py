# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from base import Base

__author__ = 'D.Kalpakchi'


class UpdateMoviesStats(Base):
    __tablename__ = u's_update_movies_stats'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    detected = sa.Column('detected', sa.Numeric(10, 0))
    existed = sa.Column('existed', sa.Numeric(10, 0))
    not_recognized = sa.Column('not_recognized', sa.Numeric(10, 0))
    stored = sa.Column('stored', sa.Numeric(10, 0))
    status = sa.Column('status', sa.String(8))
    dt_create = sa.Column('dt_create', sa.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, detected, existed, not_recognized, stored, status):
        self.detected = detected
        self.existed = existed
        self.not_recognized = not_recognized
        self.stored = stored
        self.status = status

    def __repr__(self):
        return u"<%s(d%s:e%s:nr%s:s%s)>" % (self.dt_create, self.detected, 
            self.existed, self.not_recognized, self.stored)

    def __unicode__(self):
        return self.__repr__()
