# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from ..base import Base

__author__ = 'D.Ivanets'


class CompanyPaymentSystem(Base):
    __tablename__ = u'ps_company_payment_system'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    payment_system_id = sa.Column('payment_system_id',
                                  sa.Numeric(3, 0),
                                  sa.ForeignKey('ps_payment_system.id'))
    company_id = sa.Column('company_id',
                           sa.Numeric(10, 0),
                           sa.ForeignKey('c_company.id'))
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))
    dt_created = sa.Column('dt_created',
                           sa.DateTime,
                           default=datetime.datetime.utcnow)

    payment_system = relationship('PaymentSystem')
    company = relationship('Company')
    user = relationship('User')

    linkpoint = relationship('LinkPoint', uselist=False)
    firstdata = relationship('FirstData', uselist=False)

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @property
    def system(self):
        if self.payment_system_id == 1:
            return self.linkpoint
        elif self.payment_system_id == 2:
            return self.firstdata
        else:
            return None

    def check_amount(self, card, amount):
        return self.system.check_amount(card, amount)

    def preauth_deal(self, deal):
        return self.system.preauth_deal(deal)
