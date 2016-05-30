# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sqlalchemy as sa
from ..base import Base

__author__ = 'D.Ivanets'


class OrderingType(Base):
    __tablename__ = 'e_ordering_type'

    id = sa.Column('id', sa.Numeric(2, 0), primary_key=True, )
    alias = sa.Column('alias', sa.String(10))
    name = sa.Column('name', sa.String(32))

    def __repr__(self):
        return '<%s(%s:\'%s\')>' % (self.__class__.__name__, self.id, self.name)
