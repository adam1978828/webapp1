# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session
from ..base import Base

__author__ = 'D.Ivanets'


cut_number = lambda x: x[:4]+len(x[4:-4])*'*'+x[-4:]
possible_card_exp_messages = [
    'No credit card expiration year provided.',
    'No credit card expiration year provided. (Received from DB)',
    'Credit card is expired.',
    'SGS-002304: Credit card is expired.',
]


class LinkpointTransactions(Base):
    __tablename__ = u'ps_linkpoint_transactions'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    linkpoint_id = sa.Column('linkpoint_id', sa.Numeric(10, 0), sa.ForeignKey('ps_linkpoint.id'))
    deal_id = sa.Column('deal_id', sa.String(32), sa.ForeignKey('c_deal.id'))
    CommercialServiceProvider = sa.Column('commercial_service_provider', sa.String(16), default='')
    TransactionTime = sa.Column('transaction_time', sa.String(24), default='')
    ProcessorReferenceNumber = sa.Column('processor_reference_number', sa.String(10), default='')
    ProcessorResponseMessage = sa.Column('processor_response_message', sa.String(32), default='')
    ProcessorResponseCode = sa.Column('processor_response_code', sa.String(1), default='')
    ProcessorApprovalCode = sa.Column('processor_approval_code', sa.String(16), default='')
    ErrorMessage = sa.Column('error_message', sa.String(128), default='')
    OrderId = sa.Column('order_id', sa.String(100), default='')
    ApprovalCode = sa.Column('approval_code', sa.String(64), default='')
    AVSResponse = sa.Column('avs_response', sa.String(1), default='')
    TDate = sa.Column('t_date', sa.String(10), default='')
    TransactionResult = sa.Column('transaction_result', sa.String(8), default='')
    TransactionID = sa.Column('transaction_id', sa.String(12), default='')
    CalculatedTax = sa.Column('calculated_tax', sa.String(1), default='')
    CalculatedShipping = sa.Column('calculated_shipping', sa.String(1), default='')
    TransactionScore = sa.Column('transaction_score', sa.String(10), default='')
    AuthenticationResponseCode = sa.Column('authentication_response_code', sa.String(3), default='')
    FraudAction = sa.Column('fraud_action', sa.String(30), default='')

    Type = sa.Column('type', sa.String(16))
    ChargeTotal = sa.Column('charge_total', sa.String(16))
    CardNumber = sa.Column('card_number', sa.String(19))

    linkpoint = relationship('LinkPoint')
    deal = relationship('Deal')

    def __init__(self, lp, response=None, deal=None, transaction_type=None, charge_total=None, card_number=None):
        self.linkpoint = lp
        self.deal = deal
        self.Type = transaction_type
        self.ChargeTotal = str(charge_total) if charge_total is not None else None
        self.CardNumber = cut_number(card_number) if card_number else card_number
        if response:
            self.import_from_response(response)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    def import_from_response(self, response):
        for key, value in response.items():
            if isinstance(value, str) or isinstance(value, unicode):
                self.__setattr__(key, value.strip())

    @property
    def pretty_charge_total(self):
        return float(self.ChargeTotal) if self.ChargeTotal else 0

    @property
    def is_can_be_postauthorized(self):
        if self.Type != 'preAuth':
            return False
        else:
            obj = object_session(self)\
                .query(LinkpointTransactions)\
                .filter_by(OrderId=self.OrderId)\
                .filter_by(Type='postAuth').first()
            if obj:
                return False
            else:
                return True

    @property
    def is_card_expired(self):
        return self.ErrorMessage in possible_card_exp_messages

    @property
    def is_approved(self):
        return self.TransactionResult == u'APPROVED'
