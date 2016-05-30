# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ..base import Base

__author__ = 'D.Ivanets'


class DiskCondition(Base):
    __tablename__ = u'e_disk_condition'
    __table_args__ = {'sqlite_autoincrement': True}
    id = sa.Column('id', sa.Numeric(1, 0), primary_key=True)
    value = sa.Column('value', sa.String(10))

    def __init__(self, value=''):
        self.value = value

    def __repr__(self):
        return u"<%s(%s:'%s')>" % (self.__class__.__name__, self.id, self.value)

    def __unicode__(self):
        return self.__repr__()
