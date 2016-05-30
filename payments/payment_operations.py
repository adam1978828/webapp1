# -*- coding: utf-8 -*-
import datetime

import firstdata
from payments_exceptions import *

__author__ = 'Denis Ivanets (denself@gmail.com'


class PaymentOperations(object):

    """
    possible responses:

    Approved
    Invalid Expiration Date

    Server Error. Please contact Support. (19) - Unable to Process Transaction.
    Unauthorized Request. Bad or missing credentials.
    Bad Request (22) - Invalid Credit Card Number
    Bad Request (25) - Invalid Expiry Date
    Bad Request (26) - Invalid Amount
    Bad Request (27) - Invalid Card Holder
    Bad Request (28) - Invalid Authorization Number
    Bad Request (64) - Invalid Refund
    Bad Request (69) - Invalid Transaction Tag
    """
    #
    # FIRST_DATA_GATEWAY_ID = 'AJ3548-05'
    # FIRST_DATA_PASSWORD = '99i8wy0l4aa742m487uh3qji94y784tb'
    # FIRST_DATA_KEY_ID = '265010'
    # FIRST_DATA_HMAC_KEY = 'FRhHa7PMsw2_523gY8o_8HAWfg8SKuWu'

    # FIRST_DATA_GATEWAY_ID = 'AF9729-01'
    # FIRST_DATA_PASSWORD = '7ix3jap1d72a805yv92tm2081f96os01'
    # FIRST_DATA_KEY_ID = '163445'
    # FIRST_DATA_HMAC_KEY = 'OIljLBZb9fmjWpin07aQSO1uaOzr9bgT'

    FIRST_DATA_GATEWAY_ID = u'C31203-01'
    FIRST_DATA_PASSWORD = u'5jfh5230'
    FIRST_DATA_KEY_ID = u'244880'
    FIRST_DATA_HMAC_KEY = u'wxHtwh1JC7dqV5rrXjQEPBOka78DJcdT'
    #
    # FIRST_DATA_GATEWAY_ID = u'D16880-01'
    # FIRST_DATA_PASSWORD = u'7o5fwi8d1e0f4s3uzepqbqt3tn7di0ar'
    # FIRST_DATA_KEY_ID = u'346676'
    # FIRST_DATA_HMAC_KEY = u'9PFco~ZX5B4Ty7_W8lw9oKa~JlZRry9Q'

    def __init__(self, cc_number, cc_expiry, cardholder_name):
        """
        :param cc_number: The customer's credit card number. Not used for tagged transaction types.
        :param cc_expiry: The credit card expiry date in the format mmyy. Property for manually entering expiry date.
        :param cardholder_name: The customer's name. The following characters will be stripped from this field:
            ; ` " / % as well as -- (2 consecutive dashes).
        :return:
        """
        self.cc_number = str(cc_number)
        self.cc_expiry = str(cc_expiry)
        self.cardholder_name = str(cardholder_name)
        # self._validate_card()
        self.last_authorization_num = ''
        self.last_transaction_tag = ''
        self.last_amount = ''
        self.test = False

    def _save_result(self, result):
        """
        Method, saves details of last transaction for future processes
        :param result: Server response in dict format.
        :return:
        """
        if result.get('transaction_approved', ''):
            self.last_amount = result.get('amount', '')
            self.last_authorization_num = result.get('authorization_num', '')
            self.last_transaction_tag = result.get('transaction_tag', '')

    def _validate_card(self):
        def digits_of(n):
            return [int(c) for c in str(n)]
        digits = digits_of(self.cc_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        if checksum % 10:
            raise InvalidCreditCardNumber(self.cc_number)
        if int(self.cc_expiry[:2]) > 12 or int(self.cc_expiry[:2]) == 0:
            raise InvalidExpiryDate(self.cc_expiry)
        now = datetime.datetime.utcnow()
        date = str(now.year)[-2:] + str(now.month).zfill(2)
        if date > self.cc_expiry[-2:] + self.cc_expiry[:2]:
            raise InvalidExpiryDate(self.cc_expiry)

    def fd_purchase(self, amount):
        """
        Purchase -
            The method by which an amount of funds moving from clients credit card to merchants account
            Supports "Refund transaction", "Void transaction".
        :param amount: Dollar amount.
        :type amount: float
        :return: Server response.
        :rtype: dict
        """
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='00',
                                          amount=amount,
                                          cc_number=self.cc_number,
                                          cc_expiry=self.cc_expiry,
                                          cardholder_name=self.cardholder_name)
        result = transaction.process(test=self.test)
        # p_error_check(result)
        self._save_result(result)

        return result

    def fd_pre_authorization(self, amount):
        """
        Pre-authorization -
            The method by which an amount of funds is reserved for a period of time to await sales completion.
            Supports "Complete transaction", "Void transaction".
        :param amount: Dollar amount.
        :return: Server response in dict format.
        """
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='01',
                                          amount=amount,
                                          cc_number=self.cc_number,
                                          cc_expiry=self.cc_expiry,
                                          cardholder_name=self.cardholder_name)
        result = transaction.process(test=self.test)

        self._save_result(result)

        return result

    def fd_pre_authorization_completion(self, amount='', authorization_num=''):
        """
        Pre-authorization completion -
            The method which completes pre-authorization and moving reserved amount of founds from clients credit card
            to merchants account.
            Supports "Refund transaction", "Void transaction".
        :param amount: Dollar amount.
        :param authorization_num: This is the authorization number returned by the cardholder's financial institution
            when a transaction has been approved. This value overrides any value sent for the Request Property of the
            same name.
        :return: Server response in dict format.
        """
        if amount == '':
            amount = self.last_amount
        if authorization_num == '':
            authorization_num = self.last_authorization_num
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='02',
                                          amount=amount,
                                          cc_number=self.cc_number,
                                          cc_expiry=self.cc_expiry,
                                          cardholder_name=self.cardholder_name,
                                          authorization_num=authorization_num)
        result = transaction.process(test=self.test)
        p_error_check(result)

        self._save_result(result)

        return result

    def fd_refund(self, amount=''):
        """
        Refund completion -
            The repayment to the purchaser of the total charge or a portion of that charge.
            Supports "Void transaction".
        :param amount: Dollar amount.
        :return: Server response in dict format.
        """
        if amount == '':
            amount = self.last_amount
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='04',
                                          amount=amount,
                                          cc_number=self.cc_number,
                                          cc_expiry=self.cc_expiry,
                                          cardholder_name=self.cardholder_name)
        result = transaction.process(test=self.test)
        p_error_check(result)

        self._save_result(result)

        return result

    def fd_authorization(self, amount='0'):
        """
        Authorization -
            The process by which the credit card company and/or bank permits the payment transaction to proceed.
        :return: Server response in dict format.
        """
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='05',
                                          amount=amount,
                                          cc_number=self.cc_number,
                                          cc_expiry=self.cc_expiry,
                                          cardholder_name=self.cardholder_name)
        result = transaction.process(test=self.test)
        # p_error_check(result)
        return result

    def fd_void(self, amount='', authorization_num=''):
        """
        Void -
            Cancels transaction
        :param amount: Dollar amount.
        :param authorization_num: This is the authorization number returned by the cardholder's financial institution
            when a transaction has been approved. This value overrides any value sent for the Request Property of the
            same name.
        :return: Server response in dict format.
        """
        if amount == '':
            amount = self.last_amount
        if authorization_num == '':
            authorization_num = self.last_authorization_num
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='13',
                                          amount=amount,
                                          cc_number=self.cc_number,
                                          cc_expiry=self.cc_expiry,
                                          cardholder_name=self.cardholder_name,
                                          authorization_num=authorization_num)
        result = transaction.process(test=self.test)
        # p_error_check(result)
        return result

    def fd_tagged_pre_authorization_completion(self, transaction_tag='', amount='', authorization_num=''):
        """
        Tagged Pre-authorization completion -
            The method which completes pre-authorization and moving reserved amount of founds from clients credit card
            to merchants account using tag from a last transaction.
            Supports "Refund transaction", "Void transaction".
        :param transaction_tag: A unique identifier to associate with a tagged transaction.
            This value overrides any value sent for the Request Property of the same name.
        :param amount: Dollar amount
        :param authorization_num: This is the authorization number returned by the cardholder's financial institution
            when a transaction has been approved.
            This value overrides any value sent for the Request Property of the same name.
        :return: Server response in dict format.
        """
        if amount == '':
            amount = self.last_amount
        if authorization_num == '':
            authorization_num = self.last_authorization_num
        if transaction_tag == '':
            transaction_tag = self.last_transaction_tag
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='32',
                                          amount=amount,
                                          transaction_tag=transaction_tag,
                                          authorization_num=authorization_num)
        result = transaction.process(test=self.test)
        p_error_check(result)

        self._save_result(result)

        return result

    def fd_tagged_void(self, transaction_tag='', amount='', authorization_num=''):
        """
        Tagged void -
            Cancels transaction using tag from a last transaction.
        :param transaction_tag: A unique identifier to associate with a tagged transaction.
            This value overrides any value sent for the Request Property of the same name.
        :param amount: Dollar amount
        :param authorization_num: This is the authorization number returned by the cardholder's financial institution
            when a transaction has been approved.
            This value overrides any value sent for the Request Property of the same name.
        :return: Server response in dict format.
        """
        if amount == '':
            amount = self.last_amount
        if authorization_num == '':
            authorization_num = self.last_authorization_num
        if transaction_tag == '':
            transaction_tag = self.last_transaction_tag
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='33',
                                          amount=amount,
                                          transaction_tag=transaction_tag,
                                          authorization_num=authorization_num)
        result = transaction.process(test=self.test)
        # p_error_check(result)
        return result

    def fd_tagged_refund(self, transaction_tag='', amount='', authorization_num=''):
        """
        Tagged refund completion -
            The repayment to the purchaser of the total charge or a portion of that charge.
            Supports "Void transaction".
        :param transaction_tag: A unique identifier to associate with a tagged transaction.
            This value overrides any value sent for the Request Property of the same name.
        :param amount: Dollar amount
        :param authorization_num: This is the authorization number returned by the cardholder's financial institution
            when a transaction has been approved.
            This value overrides any value sent for the Request Property of the same name.
        :return: Server response in dict format.
        """
        if amount == '':
            amount = self.last_amount
        if authorization_num == '':
            authorization_num = self.last_authorization_num
        if transaction_tag == '':
            transaction_tag = self.last_transaction_tag
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='34',
                                          amount=amount,
                                          transaction_tag=transaction_tag,
                                          authorization_num=authorization_num)
        result = transaction.process(test=self.test)
        p_error_check(result)

        self._save_result(result)

        return result


class TransArmorOperations(object):

    # FIRST_DATA_GATEWAY_ID = settings.FIRST_DATA_GATEWAY_ID  # u'C31203-01'
    # FIRST_DATA_PASSWORD = settings.FIRST_DATA_PASSWORD      # u'5jfh5230'
    # FIRST_DATA_KEY_ID = settings.FIRST_DATA_KEY_ID          # u'244880'
    # u'wxHtwh1JC7dqV5rrXjQEPBOka78DJcdT'
    # FIRST_DATA_HMAC_KEY = settings.FIRST_DATA_HMAC_KEY
    # test = settings.FIRST_DATA_TEST                         # False

    FIRST_DATA_GATEWAY_ID = 'AF9729-01'
    FIRST_DATA_PASSWORD = '7092u2yb'
    FIRST_DATA_KEY_ID = '163445'
    FIRST_DATA_HMAC_KEY = '0a7YUwo4Ngfaww~jwfJ3v8tJTuIhE4R3'
    test = False

    def ta_purchase(self, card, amount, reference_no='', customer_ref='', reference_3=''):
        """
        # Purchase -
        #     The method by which an amount of funds moving from clients credit card to merchants account
        #     Supports "Refund transaction", "Void transaction".
        #
        # :param cardholder_name: The customer's name. The following characters will be stripped from this field:
        #     ; ` " / % as well as -- (2 consecutive dashes).
        # :param transarmor_token:
        # :param amount: Dollar amount.
        # :param credit_card_type:
        # :param cc_expiry: The credit card expiry date in the format mmyy. Property for manually entering expiry date.
        # :return:
        """

        cardholder_name = card.name
        transarmor_token = card.ta_token
        credit_card_type = card.card_type
        cc_expiry = card.period
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='00',
                                          cardholder_name=cardholder_name,
                                          transarmor_token=transarmor_token,
                                          amount=amount,
                                          credit_card_type=credit_card_type,
                                          cc_expiry=cc_expiry,
                                          reference_no=reference_no,
                                          customer_ref=customer_ref,
                                          reference_3=reference_3,)
        result = transaction.process(test=self.test)

        return result

    def ta_pre_authorization(self, card, amount, reference_no='', customer_ref='', reference_3=''):
        """
        # Pre-authorization -
        #     The method by which an amount of funds is reserved for a period of time to await sales completion.
        #     Supports "Complete transaction", "Void transaction".
        #
        # :param cardholder_name: The customer's name. The following characters will be stripped from this field:
        #     ; ` " / % as well as -- (2 consecutive dashes).
        # :param transarmor_token:
        # :param amount: Dollar amount.
        # :param credit_card_type:
        # :param cc_expiry: The credit card expiry date in the format mmyy. Property for manually entering expiry date.
        # :return:
        """
        cardholder_name = card.name
        transarmor_token = card.ta_token
        credit_card_type = card.card_type
        cc_expiry = card.period
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='01',
                                          cardholder_name=cardholder_name,
                                          transarmor_token=transarmor_token,
                                          amount=amount,
                                          credit_card_type=credit_card_type,
                                          cc_expiry=cc_expiry,
                                          reference_no=reference_no,
                                          customer_ref=customer_ref,
                                          reference_3=reference_3,)
        result = transaction.process(test=self.test)

        return result

    def ta_pre_authorization_completion(self, card, amount, authorization_num):
        """
        # Pre-authorization completion -
        #     The method which completes pre-authorization and moving reserved amount of founds from clients credit card
        #     to merchants account.
        #     Supports "Refund transaction", "Void transaction".
        # :param cardholder_name:
        # :param transarmor_token:
        # :param amount: Dollar amount.
        # :param credit_card_type:
        # :param authorization_num: This is the authorization number returned by the cardholder's financial institution
        #     when a transaction has been approved. This value overrides any value sent for the Request Property of the
        #     same name.
        # :param cc_expiry:
        # :return:
        """
        cardholder_name = card.name
        transarmor_token = card.ta_token
        credit_card_type = card.card_type
        cc_expiry = card.period
        transaction = firstdata.FirstData(self.FIRST_DATA_KEY_ID, self.FIRST_DATA_HMAC_KEY,
                                          gateway_id=self.FIRST_DATA_GATEWAY_ID,
                                          password=self.FIRST_DATA_PASSWORD,
                                          transaction_type='32',
                                          cardholder_name=cardholder_name,
                                          transarmor_token=transarmor_token,
                                          amount=amount,
                                          credit_card_type=credit_card_type,
                                          authorization_num=authorization_num,
                                          cc_expiry=cc_expiry)
        result = transaction.process(test=self.test)

        return result
