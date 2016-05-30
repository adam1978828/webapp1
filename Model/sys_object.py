# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class SysObject(Base):
    __tablename__ = u'p_object'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(5, 0), primary_key=True)
    name = sa.Column('name', sa.String(128))

    functions = relationship('SysFunction')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
