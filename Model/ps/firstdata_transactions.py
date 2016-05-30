# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
import decimal
import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session
from ..base import Base

__author__ = 'D.Ivanets'


cut_number = lambda x: x[:4]+len(x[4:-4])*'*'+x[-4:]

pretty_type_map = {
    '00': "Add'l Capture",
    '01': "PreAuth",
    '32': "Capture",
    '33': "Void",
    '34': "Return",
}


class FirstdataTransactions(Base):
    __tablename__ = u'ps_firstdata_transactions'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    void_transaction_id = sa.Column('void_transaction_id',
                                    sa.Numeric(10, 0),
                                    sa.ForeignKey('ps_firstdata_transactions.id'))
    postauth_transaction_id = sa.Column(
        'postauth_transaction_id',
        sa.Numeric(10, 0),
        sa.ForeignKey('ps_firstdata_transactions.id')
    )
    return_transaction_id = sa.Column('return_transaction_id',
                                    sa.Numeric(10, 0),
                                    sa.ForeignKey('ps_firstdata_transactions.id'))
    deal_id = sa.Column('deal_id', sa.String(32), sa.ForeignKey('c_deal.id'))
    firstdata_id = sa.Column('firstdata_id', sa.Numeric(10, 0), sa.ForeignKey('ps_firstdata.id'))

    amount = sa.Column('amount', sa.Numeric(10, 2), nullable=True, default=None)
    authorization_num = sa.Column('authorization_num', sa.String(10), default='')
    bank_message = sa.Column('bank_message', sa.String(80), default='')
    bank_resp_code = sa.Column('bank_resp_code', sa.String(3), default='')
    cardholder_name = sa.Column('cardholder_name', sa.String(30), default='')
    cc_expiry = sa.Column('cc_expiry', sa.String(4), default='')
    client_ip = sa.Column('client_ip', sa.String(15), default='')
    credit_card_type = sa.Column('credit_card_type', sa.String(30), default='')
    currency_code = sa.Column('currency_code', sa.String(3), default='')
    cvd_presence_ind = sa.Column('cvd_presence_ind', sa.String(1), default='')
    exact_message = sa.Column('exact_message', sa.String(50), default='')
    exact_resp_code = sa.Column('exact_resp_code', sa.String(2), default='')
    partial_redemption = sa.Column('partial_redemption', sa.Boolean, default=False)
    retrieval_ref_no = sa.Column('retrieval_ref_no', sa.String(13), default='')
    reference_no = sa.Column('reference_no', sa.String(20), default='')
    sequence_no = sa.Column('sequence_no', sa.String(10), default='')
    transaction_approved = sa.Column('transaction_approved', sa.Boolean, default=False)
    transaction_error = sa.Column('transaction_error', sa.Boolean, default=False)
    transaction_tag = sa.Column('transaction_tag', sa.Numeric(13))
    transaction_type = sa.Column('transaction_type', sa.String(2), default='')
    transarmor_token = sa.Column('transarmor_token', sa.String(30), default='')
    card_number = sa.Column('card_number', sa.String(19))
    dt_create = sa.Column('dt_create', sa.DateTime, default=datetime.utcnow)

    firstdata = relationship('FirstData')
    deal = relationship('Deal')
    # void_transaction = relationship('FirstdataTransactions',
    #                                 foreign_keys=void_transaction_id,
    #                                 remote_side=[id],
    #                                 backref='voids')
    # postauth_transaction_id = relationship('FirstdataTransactions',
    #                                        foreign_keys=postauth_transaction_id,
    #                                        primaryjoin="User.id==Address.user_id",
    #                                        remote_side=[id],
    #                                        backref='postauths')
    # return_transaction = relationship('FirstdataTransactions',
    #                                   foreign_keys=return_transaction_id,
    #                                   remote_side=[id],
    #                                   backref='returns')

    def __init__(self, fd, response=None, deal=None, card_number=None, amount=None):
        self.firstdata = fd
        self.deal = deal
        self.card_number = cut_number(card_number) if card_number else ''
        if response:
            self.import_from_response(response)
        if amount:
            self.amount = amount

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    def import_from_response(self, response):
        self.amount = float(response.get('amount', 0))
        for key, value in response.items():
            if key not in self.__class__.__dict__: continue
            column_type = self.__class__.__dict__[key].property.columns[0].type
            self.__setattr__(key, field_serializer(column_type, value))

    @property
    def pretty_type(self):
        return pretty_type_map.get(self.transaction_type)

    @property
    def pretty_charge_total(self):
        return float(self.amount) if self.amount else 0

    # @property
    # def pretty_charge_total(self):
    #     return float(self.ChargeTotal) if self.ChargeTotal else 0

    # @property
    # def is_can_be_postauthorized(self):
    #     if self.Type != 'preAuth':
    #         return False
    #     else:
    #         obj = object_session(self)\
    #             .query(FirstdataTransactions)\
    #             .filter_by(OrderId=self.OrderId)\
    #             .filter_by(Type='postAuth').first()
    #         if obj:
    #             return False
    #         else:
    #             return True

    @property
    def is_card_expired(self):
        return False

    @property
    def is_approved(self):
        return self.transaction_approved

    @property
    def void_transactions(self):
        if self.transaction_type == '33':
            return None
        return self.firstdata.transactions \
            .filter(FirstdataTransactions.transaction_type == '33') \
            .filter(FirstdataTransactions.void_transaction_id == self.id) \
            .all()

    @property
    def postauth_transactions(self):
        if self.transaction_type != '01':
            return None
        return self.firstdata.transactions \
            .filter(FirstdataTransactions.transaction_type == '32') \
            .filter(FirstdataTransactions.postauth_transaction_id == self.id) \
            .all()

    @property
    def return_transactions(self):
        if self.transaction_type == '34':
            return None
        return self.firstdata.transactions \
            .filter(FirstdataTransactions.transaction_type == '34') \
            .filter(FirstdataTransactions.return_transaction_id == self.id) \
            .all()

def field_serializer(field, data):

    if isinstance(field, sa.String):
        if data is None:
            return data
        return str(data)[:field.length]
    elif isinstance(field, sa.Numeric):
        return Decimal(data)
    elif isinstance(field, sa.Boolean):
        return bool(data)
