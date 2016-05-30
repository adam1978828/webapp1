# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class Transaction(Base):
    __tablename__ = u'c_transaction'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric, primary_key=True)
    dt = sa.Column('dt', sa.DateTime)
    amount = sa.Column('amount', sa.Numeric(12, 2))
    transaction_type_id = sa.Column(
        'transaction_type_id', sa.Numeric(2, 0), sa.ForeignKey('e_transaction_type.id'))
    deal_id = sa.Column('deal_id', sa.Numeric, sa.ForeignKey('c_deal.id'))
    dt_modify = sa.Column(
        'dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    card_id = sa.Column('card_id', sa.String(36), sa.ForeignKey('c_card.id'))
    authorization_number = sa.Column(
        'authorization_number', sa.String(10), default='')
    bank_message = sa.Column('bank_message', sa.String(80), default='')
    bank_resp_code = sa.Column('bank_resp_code', sa.String(3), default='')
    exact_message = sa.Column('exact_message', sa.String(50), default='')
    exact_resp_code = sa.Column('exact_resp_code', sa.String(2), default='')
    client_ip = sa.Column('client_ip', sa.String(15), default='')
    gateway_id = sa.Column('gateway_id', sa.String(10), default='')
    partial_redemption = sa.Column(
        'partial_redemption', sa.Boolean, default=False)
    retrieval_ref_no = sa.Column('retrieval_ref_no', sa.String(13), default='')
    sequence_no = sa.Column('sequence_no', sa.String(50), default='')
    transaction_approved = sa.Column(
        'transaction_approved', sa.Boolean, default=True)
    transaction_error = sa.Column(
        'transaction_error', sa.Boolean, default=False)
    transaction_tag = sa.Column('transaction_tag', sa.Numeric(12, 0))
    transaction_type = sa.Column('transaction_type', sa.String(2), default='')
    transarmor_token = sa.Column('transarmor_token', sa.String(20), default='')

    # transaction_type = relationship('TransactionType', backref='transactions')
    # deal = relationship('Deal', backref='transactions')
    card = relationship('Card', backref='transactions')

    def __init__(self):
        pass

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
