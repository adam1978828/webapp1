# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class UserToGroup(Base):
    __tablename__ = u'p_user_to_group'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    group_id = sa.Column(
        'group_id', sa.Numeric(5, 0), sa.ForeignKey('p_group.id'))
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))

    user = relationship('User')
    group = relationship('Group')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
