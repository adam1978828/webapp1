# -*- coding: utf-8 -*-
import pytz
import sqlalchemy as sa
from ..base import Base

__author__ = 'D.Ivanets'


class Timezone(Base):
    __tablename__ = u'e_timezone'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(3, 0), primary_key=True)
    name = sa.Column('name', sa.String(32), default='')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.id, self.name)

    def __unicode__(self):
        return self.__repr__()

    @property
    def tz_info(self):
        return pytz.timezone(self.name)
