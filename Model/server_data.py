# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base

__author__ = 'D.Ivanets'


class ServerData(Base):
    __tablename__ = u's_server_data'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(1, 0), primary_key=True)
    dt_last_payment = sa.Column('dt_last_payment', sa.DateTime)

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
