# -*- coding: utf-8 -*-
from decimal import localcontext, BasicContext, Decimal
import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session

from ..base import Base, ExtMixin
from payment_gateways.firstdata import FirstData as ps
from firstdata_transactions import FirstdataTransactions


__author__ = u'D.Ivanets'


pre_auth_status_map = {
    101: 201,  # NEW RENT -> PREAUTH RENT
    102: 202,  # NEW SALE -> PREAUTH SALE
    321: 311,  # NA EJECTED RENT -> EJECTED RENT
    231: 241,  # NEW RESERVATION -> PREAUTH RESERVED
}


class FirstData(Base):
    __tablename__ = u'ps_firstdata'
    __table_args__ = {}
    id = sa.Column(u'id', sa.Numeric(10, 0), primary_key=True)
    cps_id = sa.Column(u'cps_id', sa.Numeric(10, 0),
                       sa.ForeignKey(u'ps_company_payment_system.id'))

    gateway_id = sa.Column(u'gateway_id', sa.String(32), default='')
    password = sa.Column(u'password', sa.String(32), default='')
    key_id = sa.Column(u'key_id', sa.String(32), default='')
    hmac_key = sa.Column(u'hmac_key', sa.String(32), default='')

    is_test = sa.Column(u'is_test', sa.Boolean, default=False)

    company_payment_system = relationship(u'CompanyPaymentSystem')
    transactions = relationship(u'FirstdataTransactions',
                                order_by=u'FirstdataTransactions.id',
                                lazy=u'dynamic')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    # @property
    # def normalized(self):
    #     return {u'name': self.company_payment_system.payment_system.name,
    #             u'account_number': self.username,
    #             u'creator': self.company_payment_system.user}

    # @property
    # def store_number(self):
    #     return self.username[2:-4]
    @property
    def account(self):
        return self.gateway_id

    def init_processor(self):
        return ps(key=self.key_id,
                  secret=self.hmac_key,
                  gateway_id=self.gateway_id,
                  password=self.password,
                  test=self.is_test)

    def sale_transaction(self, card, amount, deal=None):
        """
        A sale transaction immediately charges a customer's credit card when
        the batch of transactions is closed.
        """
        processor = self.init_processor()
        response = processor.process(transaction_type='00',
                                     amount=round(amount, 2),
                                     cc_number=card.number,
                                     cc_expiry=card._cc_expiry,
                                     cardholder_name=card._cardholder_name)

        kiosk_name = deal.kiosk_start.settings.alias if deal else u''

        fdt = FirstdataTransactions(self,
                                    response=response,
                                    deal=deal,
                                    card_number=card.number)
        object_session(self).add(fdt)
        session = object_session(self)
        session.add(fdt)
        session.commit()
        session.refresh(fdt)
        return fdt

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
        kiosk_name = deal.kiosk_start.settings.alias if deal else ''

        response = processor.process(transaction_type='01',
                                     cc_number=card.number,
                                     cc_expiry=card._cc_expiry,
                                     cardholder_name=card._cardholder_name,
                                     amount=amount)
        fdt = FirstdataTransactions(self,
                                    response=response,
                                    deal=deal,
                                    card_number=card.number)
        session = object_session(self)
        session.add(fdt)
        session.commit()
        session.refresh(fdt)
        return fdt

    def postauthorize_amount(self, transaction, amount):
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

        authorization_num = transaction.authorization_num
        transaction_tag = transaction.transaction_tag
        if transaction_tag:
            transaction_tag = int(transaction_tag)

        deal = transaction.deal
        kiosk_name = deal.kiosk_start.settings.alias if deal else u''
        card = deal.card

        response = processor.process(
            transaction_type='32',
            amount=round(amount, 2),
            transaction_tag=transaction_tag,
            authorization_num=authorization_num,
        )

        fdt = FirstdataTransactions(self,
                                    response=response,
                                    deal=deal,
                                    card_number=card.number)
        fdt.postauth_transaction_id = transaction.id
        session = object_session(self)
        session.add(fdt)
        session.commit()
        session.refresh(fdt)
        return fdt

    def void_transaction(self, transaction):
        """
        To void a transaction is to cancel a payment transaction. Merchants
        can void transactions prior to settlement. Once the transaction has
        settled, the merchant has to perform a return or credit to reverse
        the charges and credit the customer's card.
        """
        processor = self.init_processor()

        authorization_num = transaction.authorization_num
        transaction_tag = transaction.transaction_tag
        if transaction_tag:
            transaction_tag = int(transaction_tag)

        deal = transaction.deal
        kiosk_name = deal.kiosk_start.settings.alias if deal else u''

        response = processor.process(
            transaction_type='33',
            amount=transaction.amount,
            transaction_tag=transaction_tag,
            authorization_num=authorization_num
        )

        fdt = FirstdataTransactions(self,
                                    response=response,
                                    deal=deal)
        fdt.void_transaction_id = transaction.id
        session = object_session(self)
        session.add(fdt)
        session.commit()
        session.refresh(fdt)
        return fdt

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
        kiosk_name = deal.kiosk_start.settings.alias if deal else u''

        authorization_num = transaction.authorization_num
        transaction_tag = transaction.transaction_tag
        if transaction_tag:
            transaction_tag = int(transaction_tag)

        response = processor.process(
            transaction_type='34',
            amount=round(amount, 2),
            transaction_tag=transaction_tag,
            authorization_num=authorization_num,
        )
        fdt = FirstdataTransactions(self,
                                    response=response,
                                    deal=deal)
        fdt.return_transaction_id = transaction.id
        session = object_session(self)
        session.add(fdt)
        session.commit()
        session.refresh(fdt)
        return fdt

    def preauth_deal(self, deal):
        amount = deal.get_preauth_amount() or 0.01
        
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
        processor = self.init_processor()
        response = processor.process(transaction_type='05',
                                     amount=round(amount, 2),
                                     cc_number=card.number,
                                     cc_expiry=card._cc_expiry,
                                     cardholder_name=card._cardholder_name)
        fdt = FirstdataTransactions(self,
                                    response=response,
                                    deal=deal)
        session = object_session(self)
        session.add(fdt)
        session.commit()
        session.refresh(fdt)
        return fdt

    def active_preauth(self, deal):
        """ Return all active pre_auth transaction for requested deal
        :param deal:
        :return: List of active preauthorizations
        """

        # Get list of all postauthorized transactions on this deal
        postauth = self.transactions \
            .filter_by(deal=deal) \
            .filter_by(transaction_type='32') \
            .filter_by(transaction_approved=True) \
            .all()
        postauth = [item.postauth_transaction_id for item in postauth]

        # Get list of all approved preauthorized transactions on this deal
        query = self.transactions\
            .filter_by(deal=deal) \
            .filter_by(transaction_type='01') \
            .filter_by(transaction_approved=True)\
            .filter(FirstdataTransactions.amount > 0)
        # Exclude all postauthorized transactions
        if postauth:

            clause = FirstdataTransactions.id.notin_(postauth)
            query = query.filter(clause)

        return query.all()

    def deal_total_charged(self, deal):
        localcontext(BasicContext)
        v_list = self.transactions \
            .filter_by(deal=deal) \
            .filter_by(transaction_type='33')\
            .filter_by(transaction_approved=True).all()
        v_list = [item.transaction_tag for item in v_list]

        t_list = self.transactions \
            .filter_by(deal=deal) \
            .filter(FirstdataTransactions.transaction_type.in_(['00', '32'])) \
            .filter_by(transaction_approved=True).all()
        t_list = [item.amount for item in t_list if item.transaction_tag not in v_list]

        r_list = self.transactions \
            .filter_by(deal=deal) \
            .filter_by(transaction_type='34')\
            .filter_by(transaction_approved=True).all()
        r_list = [item.amount for item in r_list if item.transaction_tag not in v_list]

        return float(((sum(t_list) or Decimal(0)) - (sum(r_list) or Decimal(0))).quantize(Decimal('0.01')))

    def deal_total_preauth(self, deal):
        postauth_list = self.transactions \
            .filter_by(deal=deal) \
            .filter_by(transaction_type='32') \
            .filter_by(transaction_approved=True).all()
        postauth_list = [p.OrderId for p in postauth_list]

        preauth_list = self.transactions \
            .filter_by(deal=deal) \
            .filter_by(transaction_type='01') \
            .filter_by(transaction_approved=True).all()
        preauth_list = [item for item in preauth_list
                        if item.transaction_tag not in postauth_list]
        return sum(float(item.amount) for item in preauth_list)

    def process_amount_for_deal(self, deal):
        amount = float(deal.total_amount) - float(self.deal_total_charged(deal))

        # First of all we have to close all open preauthorizations.
        for t in self.active_preauth(deal):

            # Calculate amount, that will b postauthorized
            charge = amount
            # We can not postauthorize more, then preauthorized.
            if float(t.amount) < amount or amount <= 0:
                charge = float(t.amount)

            res_post = self.postauthorize_amount(t, charge)

            # Check result
            # alr_post_mess = 'POSTAUTH already performed for this transaction.'
            if res_post.transaction_approved:
                amount = round(amount - charge, 2)
                if amount < 0:
                    void_res = self.void_transaction(res_post)

                    if void_res.transaction_approved:
                        amount = round(amount + charge, 2)
            # TODO: find out that message
            # elif alr_post_mess in res_post.get('ErrorMessage', ''):
            #     # This post auth were already performed, so lets just modify
            #     # this transaction result to APPROVED
            #     post_transaction = deal.linkpoint_transaction_lazy\
            #         .filter_by(Type='postAuth')\
            #         .filter_by(OrderId=t.OrderId).one()
            #     post_transaction.TransactionResult = 'APPROVED'
            #     post_transaction.ErrorMessage += ' (Manual approved)'
            #     amount = round(amount - float(t.ChargeTotal), 2)

            # This case will work out, if we have to return some amount.

        # After all preauth closed, we can either catch additional amount
        if amount > 0:
            res_sale = self.sale_transaction(deal.card, amount, deal)
            if res_sale.transaction_approved:
                # TODO: if transaction not approved, should change deal status
                pass
        # Or return some amount
        elif amount < 0:
            # captured transactions
            cap_transactions = deal.firstdata_transaction_lazy \
                .filter(FirstdataTransactions.transaction_type.in_(['00', '32'])) \
                .filter_by(transaction_approved=True).all()

            for t in cap_transactions:
                if deal.firstdata_transaction_lazy\
                        .filter(FirstdataTransactions.void_transaction_id == t.id)\
                        .filter(FirstdataTransactions.transaction_approved == True)\
                        .first():
                    continue
                # captured sum
                total = float(t.amount)
                # how many can we withdraw in fact
                for tt in t.return_transactions:
                    total = round(total - float(tt.amount), 2)

                total = min(total, abs(amount))
                if total:
                    res_ret = self.return_transaction(t, total)
                    if res_ret.is_approved:
                        amount = round(amount + total, 2)
                        if not amount:
                            break
