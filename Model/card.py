# -*- coding: utf-8 -*-
import hashlib
import uuid
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from base import Base


__author__ = 'D.Ivanets'


class Card(Base):
    __tablename__ = u'c_card'
    __table_args__ = {}
    id = sa.Column('id', sa.String(32), primary_key=True)
    _n1 = sa.Column('n1', sa.String(13))
    _n2 = sa.Column('n2', sa.String(10))
    hash = sa.Column('hash', sa.String(32))
    _cc_expiry = sa.Column('cc_expiry', sa.String(4))
    _cardholder_name = sa.Column('cardholder_name', sa.String(50))
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'))
    # ta_token = sa.Column('ta_token', sa.String(30), default='')
    # card_type = sa.Column('card_type', sa.String(30), default='')
    card_status_id = sa.Column('card_status_id', sa.Numeric(2, 0), sa.ForeignKey('e_card_status.id'), default=0)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))
    is_active = sa.Column('is_active', sa.Boolean, default=True)
    dt_add = sa.Column('dt_add', sa.DateTime, default=datetime.datetime.utcnow)

    company = relationship('Company')
    card_status = relationship('CardStatus')
    user = relationship('User')

    sync_filter_rules = [lambda request: (Card.company == request.kiosk.company), ]

    def __init__(self):
        self.id = str(uuid.uuid1().hex)
        self.card_status_id = 0

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    def set_card(self, cc_number, cc_expiry, cardholder_name=''):
        cc_number = str(cc_number)
        cc_number = str(int(cc_number) * 3)
        sn1, sn2 = cc_number[:4] + cc_number[8:12], cc_number[4:8] + cc_number[12:]
        self._n1, self._n2 = sn2, sn1
        self.hash = hashlib.md5(cc_number + cc_expiry).hexdigest()
        self._cc_expiry = cc_expiry
        self._cardholder_name = cardholder_name

    @staticmethod
    def get_hash(*args):
        if len(args) > 1:
            cc_number, cc_expiry = args[0], args[1]
        else:
            res = args[0]
            cc_number, cc_expiry, cardholder_name = res['cc_number'], res['cc_expiry'], res['cardholder_name']
        cc_number = str(cc_number)
        cc_number = str(int(cc_number) * 3)
        return hashlib.md5(cc_number + cc_expiry).hexdigest()

    @property
    def number(self):
        cc_number = self._n2[:4] + self._n1[:4] + self._n2[4:] + self._n1[4:]
        cc_number = str(int(cc_number) / 3)
        return cc_number

    @property
    def value_to_display(self):
        number = self.number
        return '%s (%s...%s)' % (self._cardholder_name, number[:4], number[-4:])

    @staticmethod
    def get_hash(*args):
        if len(args) == 3:
            cc_number, cc_expiry = args
        else:
            res = args[0]
            cc_number, cc_expiry = res['cc_number'], res['cc_expiry']
        cc_number = str(cc_number)
        cc_number = str(int(cc_number) * 3)
        return hashlib.md5(cc_number + cc_expiry).hexdigest()

    def _n1_setter(self, value):
        self._n1 = value

    n1 = property(None, _n1_setter)

    def _n2_setter(self, value):
        self._n2 = value

    n2 = property(None, _n2_setter)

    def _cc_expiry_setter(self, value):
        self._cc_expiry = value

    cc_expiry = property(None, _cc_expiry_setter)

    def _cardholder_name_setter(self, value):
        self._cardholder_name = value

    cardholder_name = property(None, _cardholder_name_setter)