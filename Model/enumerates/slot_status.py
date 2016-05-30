# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ..base import Base

__author__ = 'D.Ivanets'


class SlotStatus(Base):
    __tablename__ = 'e_slot_status'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    alias = sa.Column('alias', sa.String(16), default='')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.id, self.alias)

    def __unicode__(self):
        return self.__repr__()
