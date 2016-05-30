# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base

__author__ = 'D.Ivanets'


class TransactionType(Base):
    __tablename__ = u'e_transaction_type'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric, primary_key=True)
    name = sa.Column('name', sa.String(255))

    def __repr__(self):
        return u"<%s(%s: '%s')>" % (self.__class__.__name__, self.id, self.name)

    def __unicode__(self):
        return self.__repr__()
