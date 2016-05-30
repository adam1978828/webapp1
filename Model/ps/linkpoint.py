# -*- coding: utf-8 -*-
from decimal import localcontext, BasicContext, Decimal
import os

from django.conf import settings
import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session

from ..base import Base, ExtMixin
from python_linkpoint import LinkPoint as ps
from linkpoint_transactions import LinkpointTransactions


__author__ = u'D.Ivanets'


pre_auth_status_map = {
    101: 201,  # NEW RENT -> PREAUTH RENT
    102: 202,  # NEW SALE -> PREAUTH SALE
    321: 311,  # NA EJECTED RENT -> EJECTED RENT
    231: 241,  # NEW RESERVATION -> PREAUTH RESERVED
}


class LinkPoint(Base, ExtMixin):
    __tablename__ = u'ps_linkpoint'
    __table_args__ = {}
    id = sa.Column(u'id', sa.Numeric(10, 0), primary_key=True)
    cps_id = sa.Column(u'cps_id', sa.Numeric(10, 0),
                       sa.ForeignKey(u'ps_company_payment_system.id'))
    username = sa.Column(u'username', sa.String(16), default='')
    password = sa.Column(u'password', sa.String(8), default='')
    guid = sa.Column(u'guid', sa.String(32), default=u'')
    is_test = sa.Column(u'is_test', sa.Boolean, default=False)

    company_payment_system = relationship(u'CompanyPaymentSystem')
    transactions = relationship(u'LinkpointTransactions',
                                order_by=u'LinkpointTransactions.id',
                                lazy=u'dynamic')

    def __init__(self, username, password, pay_id):
        ExtMixin.__init__(self)
        self.username = username
        self.password = password
        self.guid = pay_id

    @sa.orm.reconstructor
    def init_on_load(self): 
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @property
    def account(self):
        return self.store_number

    @property
    def normalized(self):
        return {u'name': self.company_payment_system.payment_system.name,
                u'account_number': self.username,
                u'creator': self.company_payment_system.user}

    @property
    def store_number(self):
        return self.username[2:-4]

    def init_processor(self):
        pem_file = os.path.join(settings.LINKPOINT_KEYS_DIR,
                                self.guid,
                                self.username + u'.pem')
        key_file = os.path.join(settings.LINKPOINT_KEYS_DIR,
                                self.guid,
                                self.username + u'.key')
        return ps(username=self.username,
                  password=self.password,
                  pem_file=pem_file,
                  key_file=key_file,
                  test=self.is_test)

    def sale_transaction(self, card, amount, deal=None):
        """
        A sale transaction immediately charges a customer's credit card when
        the batch of transactions is closed.
        """
        processor = self.init_processor()
        credit_card_data = {
            u'CardNumber': card.number,
            u'ExpMonth': card._cc_expiry[:2],
            u'ExpYear': card._cc_expiry[2:],
        }
        kiosk_name = deal.kiosk_start.settings.alias if deal else u''
        response = processor.process(CreditCardTxType={u'Type': u'sale'},
                                     CreditCardData=credit_card_data,
                                     Payment={u'ChargeTotal': amount},
                                     TransactionDetails={u'UserID': kiosk_name},)
        lpt = LinkpointTransactions(self,
                                    response=response,
                                    deal=deal,
                                    transaction_type=u'sale',
                                    charge_total=str(amount),
                                    card_number=card.number)
        session = object_session(self)
        session.add(lpt)
        session.commit()
        session.refresh(lpt)
        return lpt

    def preauthorize_amount(self, card, amount, deal=None):
        """
        An Authorize Only transaction reserves funds on a customer's credit
        card. An Authorize Only transaction does not charge the card until
        you perform a Ticket Only transaction and confirm shipment of the
        order using an option available in the Reports section. Authorize -
        only transactions reserve funds for varying periods, depending on the
        issuing credit card company's policy. The period may be as little as
        three days or as long as several months. For your protection, you
        should confirm shipment as soon as possible after authorization.
        """
        if deal:
            deal.preauth_amount = amount

        processor = self.init_processor()
        credit_card_data = {
            u'CardNumber': card.number,
            u'ExpMonth': card._cc_expiry[:2],
            u'ExpYear': card._cc_expiry[2:],
        }
        kiosk_name = deal.kiosk_start.settings.alias[:32] if deal else u''
        response = processor.\
            process(CreditCardTxType={u'Type': u'preAuth'},
                    CreditCardData=credit_card_data,
                    Payment={u'ChargeTotal': amount},
                    TransactionDetails={u'UserID': kiosk_name})
        lpt = LinkpointTransactions(self,
                                    response=response,
                                    deal=deal,
                                    transaction_type=u'preAuth',
                                    charge_total=str(amount),
                                    card_number=card.number)
        session = object_session(self)
        session.add(lpt)
        session.commit()
        session.refresh(lpt)
        return lpt

    def postauthorize_amount(self, transaction, amount=None):
        """
        A Ticket Only transaction is a post - authorization transaction that
        captures funds from an Authorize Only transaction. Funds are
        transferred when your batch of transactions is settled. If you enter
        a larger total for the Ticket Only transaction than was specified for
        the Authorize Only transaction, the Ticket Only transaction may be
        blocked. If you enter a smaller amount than was authorized, an
        adjustment is made to the Authorization to reserve only the smaller
        amount of funds on the customer‟s card for the transaction.
        """
        processor = self.init_processor()
        order_id = transaction.OrderId
        deal = transaction.deal
        kiosk_name = deal.kiosk_start.settings.alias[:32] if deal else u''
        response = processor.\
            process(CreditCardTxType={u'Type': u'postAuth'},
                    TransactionDetails={u'UserID': kiosk_name,
                                        u'OrderId': order_id},
                    Payment={u'ChargeTotal': amount})
        lpt = LinkpointTransactions(self,
                                    response=response,
                                    deal=deal,
                                    transaction_type=u'postAuth',
                                    charge_total=amount)
        session = object_session(self)
        session.add(lpt)
        session.commit()
        session.refresh(lpt)
        return lpt

    def void_transaction(self, transaction):
        """
        To void a transaction is to cancel a payment transaction. Merchants
        can void transactions prior to settlement. Once the transaction has
        settled, the merchant has to perform a return or credit to reverse
        the charges and credit the customer's card.
        """
        processor = self.init_processor()
        kiosk_name = transaction.deal.kiosk_start.settings.alias if \
            transaction.deal else u''
        response = processor.\
            process(CreditCardTxType={u'Type': u'void'},
                    TransactionDetails={u'OrderId': transaction.OrderId,
                                        u'UserID': kiosk_name,
                                        u'TDate': transaction.TDate})
        lpt = LinkpointTransactions(self,
                                    response=response,
                                    deal=transaction.deal,
                                    transaction_type=u'void')
        session = object_session(self)
        session.add(lpt)
        session.commit()
        session.refresh(lpt)
        return lpt

    def return_transaction(self, transaction, amount):
        """
        A Return transaction returns funds to a customer‟s credit card
        for an existing order on the system. To perform a return, you need
        the order number (which you can find in your reports). After you
        perform a Return for the full order amount, the order will appear in
        your reports with a transaction amount of 0.00.
        """
        processor = self.init_processor()
        deal = transaction.deal
        order_id = transaction.OrderId
        kiosk_name = deal.kiosk_start.settings.alias if deal else u''
        response = processor.\
            process(CreditCardTxType={u'Type': u'return'},
                    TransactionDetails={u'UserID': kiosk_name,
                                        u'OrderId': order_id},
                    Payment={u'ChargeTotal': amount})
        lpt = LinkpointTransactions(self,
                                    response=response,
                                    deal=deal,
                                    transaction_type=u'return',
                                    charge_total=amount)
        session = object_session(self)
        session.add(lpt)
        session.commit()
        session.refresh(lpt)
        return lpt

    def preauth_deal(self, deal):
        """ Preauthorize required amount for deal
        :param deal: Deal, that should be preauthorized.
        :return: transaction result and custom message in case
        """
        # Calculate preAuth amount
        amount = deal.get_preauth_amount() or 0.01
        # Process transaction
        res = self.preauthorize_amount(deal.card, amount, deal)

        # Check result
        if res.is_approved:
            # Mark card as trusted
            deal.card.card_status_id = 1
            # Change deal status
            deal.deal_status_id = pre_auth_status_map[deal.deal_status_id]
        else:
            # Error cases
            deal.deal_status_id = 404  # REJECTED
            deal.card.card_status_id = 1
            deal.kiosk_end_id = deal.kiosk_start_id
            deal.dt_end = deal.dt_start
            # If Expired credit card
            if res.is_card_expired:
                # We will mark this card as expired to disallow to user to
                # use this card again
                deal.card.card_status_id = 2
                deal.deal_status_id = 403  # FRAUD CARD
        return res

    def check_amount(self, card, amount, deal=None):
        """If customer rents list of disks, we have to check whether he has
        enough money on his account to rent all of them.
        :param card:
        :param amount:
        :param deal:
        :return:
        """
        amount = amount or 0.01
        res = self.preauthorize_amount(card, amount, deal)
        if res.is_approved:
            res_post = self.postauthorize_amount(res, amount)
            # Here is possible DECLINED response with message
            # "The server encountered a database error."
            # In this case void has no sense, but we have to report
            # somehow about it
            res_void = self.void_transaction(res_post)
        return res

    def check(self):
        processor = self.init_processor()
        return processor.check()

    def active_preauth(self, deal):
        """ Return all active pre_auth transaction for requested deal
        :param deal:
        :return: List of active preauthorizations
        """

        # Get list of all postauthorized transactions on this deal
        postauth = self.transactions \
            .filter(LinkpointTransactions.deal_id == deal.id) \
            .filter(LinkpointTransactions.Type == 'postAuth') \
            .all()
        postauth = [item.OrderId for item in postauth]

        # Get list of all approved preauthorized transactions on this deal
        query = self.transactions\
            .filter(LinkpointTransactions.deal_id == deal.id) \
            .filter(LinkpointTransactions.Type == 'preAuth') \
            .filter(LinkpointTransactions.TransactionResult == 'APPROVED')
        # Exclude all postauthorized transactions
        if postauth:
            query = query.filter(LinkpointTransactions.OrderId.notin_(postauth))

        return query.all()

    def deal_total_charged(self, deal):
        localcontext(BasicContext)
        v_list = self.transactions \
            .filter_by(deal=deal) \
            .filter_by(Type='void').all()
        v_list = [item.OrderId for item in v_list]

        t_list = self.transactions \
            .filter_by(deal=deal) \
            .filter(LinkpointTransactions.Type.in_(['sale', 'postAuth'])) \
            .filter_by(TransactionResult='APPROVED').all()
        t_list = [Decimal(str(item.ChargeTotal)) for item in t_list
                  if item.OrderId not in v_list]

        r_list = self.transactions \
            .filter_by(deal=deal) \
            .filter_by(Type='return').all()
        r_list = [Decimal(str(item.ChargeTotal)) for item in r_list
                  if item.OrderId not in v_list]

        return float(((sum(t_list) or Decimal(0)) - (sum(r_list) or Decimal(0))).quantize(Decimal('0.01')))

    def deal_total_preauth(self, deal):
        postauth_list = self.linkpoint_transaction \
            .filter_by(deal=deal) \
            .filter_by(Type='postAuth') \
            .filter_by(TransactionResult='APPROVED').all()
        postauth_list = [p.OrderId for p in postauth_list]

        preauth_list = self.linkpoint_transaction_lazy \
            .filter_by(deal=deal) \
            .filter_by(Type='preAuth') \
            .filter_by(TransactionResult='APPROVED').all()
        preauth_list = [item for item in preauth_list
                        if item.OrderId not in postauth_list]
        return sum(float(item.ChargeTotal) for item in preauth_list)

    def process_amount_for_deal(self, deal):
        # TODO properly calculate all amounts in Decimal format

        amount = float(deal.total_amount) - float(self.deal_total_charged(deal))

        # First of all we have to close all open preauthorizations.
        for t in self.active_preauth(deal):

            # Calculate amount, that will b postauthorized
            charge = amount
            # We can not postauthorize more, then preauthorized.
            if float(t.ChargeTotal) < amount or amount <= 0:
                charge = float(t.ChargeTotal)

            res_post = self.postauthorize_amount(t, charge)

            # Check result
            alr_post_mess = 'POSTAUTH already performed for this transaction.'
            if res_post.is_approved:
                amount = round(amount - charge, 2)
            elif alr_post_mess in res_post.ErrorMessage:
                # This post auth were already performed, so lets just modify
                # this transaction result to APPROVED
                post_transaction = deal.linkpoint_transaction_lazy\
                    .filter_by(Type='postAuth')\
                    .filter_by(OrderId=t.OrderId).one()
                post_transaction.TransactionResult = 'APPROVED'
                post_transaction.ErrorMessage += ' (Manual approved)'
                amount = round(amount - float(t.ChargeTotal), 2)

            # This case will work out, if we have to return some amount.
            if amount < 0:
                self.void_transaction(res_post)

                if res_post.is_approved:
                    amount = round(amount + charge, 2)

        # After all preauth closed, we can either catch additional amount
        if amount > 0:
            res_sale = self.sale_transaction(deal.card, amount, deal)
            if res_sale.is_approved:
                # TODO: if transaction not approved, should change deal status
                pass
        # Or return some amount
        elif amount < 0:
            # captured transactions
            cap_transactions = deal.linkpoint_transaction_lazy \
                .filter(LinkpointTransactions.Type.in_(['sale', 'postAuth'])) \
                .filter_by(TransactionResult='APPROVED').all()

            for t in cap_transactions:
                if deal.linkpoint_transaction_lazy\
                        .filter_by(Type='void')\
                        .filter_by(OrderId=t.OrderId).first():
                    continue
                # captured sum
                total = float(t.ChargeTotal)
                # how many can we withdraw in fact
                return_transactions = deal.linkpoint_transaction_lazy\
                    .filter_by(Type='return')\
                    .filter_by(OrderId=t.OrderId).all()

                for tt in return_transactions:
                    total = round(total - float(tt.ChargeTotal), 2)

                total = min(total, abs(amount))
                if total:
                    res_ret = self.return_transaction(t, total)
                    if res_ret.is_approved:
                        amount = round(amount + total, 2)
                        if not amount:
                            break
