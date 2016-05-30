# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ..base import Base

__author__ = 'D.Ivanets'


class DealStatus(Base):
    __tablename__ = u'e_deal_status'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(3, 0), primary_key=True)
    alias = sa.Column('alias', sa.String(16), default='')
    is_send_to_kiosk = sa.Column('is_send_to_kiosk', sa.Boolean)
    is_send_from_kiosk = sa.Column('is_send_from_kiosk', sa.Boolean)

    def __init__(self, alias=''):
        self.alias = alias

    def __repr__(self):
        return u"<%s(%s: '%s')>" % (self.__class__.__name__, self.id, self.alias)

    def __unicode__(self):
        return self.__repr__()
