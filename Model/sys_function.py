# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class SysFunction(Base):
    __tablename__ = u'p_function'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(5, 0), primary_key=True)
    name = sa.Column('name', sa.String(256), default='')
    alias = sa.Column('alias', sa.String(64), default='')
    parent_id = sa.Column(
        'parent_id', sa.Numeric(5, 0), sa.ForeignKey('p_object.id'))
    for_company = sa.Column('for_company', sa.Boolean, default=False)
    for_focus = sa.Column('for_focus', sa.Boolean, default=False)

    parent = relationship('SysObject')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
