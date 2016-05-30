# -*- coding: utf-8 -*-
import sqlalchemy as sa
# from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class GroupPermission(Base):
    __tablename__ = u'p_group_permission'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    group_id = sa.Column(
        'group_id', sa.Numeric(5, 0), sa.ForeignKey('p_group.id'))
    function_id = sa.Column(
        'function_id', sa.Numeric(5, 0), sa.ForeignKey('p_function.id'))

    # group = relationship('Group')
    # function = relationship('SysFunction')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
