# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from base import Base

__author__ = 'D.Ivanets'


class UpcSound(Base):
    __tablename__ = u'd_upc_sound'
    __table_args__ = {}
    upc = sa.Column('upc', sa.String(20), sa.ForeignKey('upc.upc'), primary_key=True)
    language_id = sa.Column('language_id', sa.Numeric, sa.ForeignKey('e_language.id'), primary_key=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
