# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ..base import Base

__author__ = 'D.Ivanets'


class CardStatus(Base):
    __tablename__ = u'e_card_status'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(2, 0), primary_key=True)
    name = sa.Column('name', sa.String(32), default='')
    alias = sa.Column('alias', sa.String(16), default='')
    description = sa.Column('description', sa.String(256), default='')
    allow_transaction = sa.Column('allow_transaction', sa.Boolean, default=True)

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.id, self.alias, )

    def __unicode__(self):
        return self.__repr__()
