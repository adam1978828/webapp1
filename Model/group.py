# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class Group(Base):
    __tablename__ = u'p_group'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(5, 0), primary_key=True)
    name = sa.Column('name', sa.String(256), default='')
    company_id = sa.Column(
        'company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'))

    company = relationship('Company')
    permissions = relationship('SysFunction', secondary='p_group_permission')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
