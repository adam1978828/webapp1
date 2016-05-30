# -*- coding: utf-8 -*-
from decimal import Decimal
from xml.etree.ElementTree import tostring, Element, SubElement
from xml.dom.minidom import parseString
import datetime

import requests

from utils import parse_xml


__author__ = 'denself'


class LinkPoint(object):
    """
    http://www.firstdata.com/downloads/marketing-merchant/fdgg-web-service-api-v6.0.pdf
    """

    OPERATIONS = ['sale', 'preAuth', 'postAuth', 'forceTicket', 'return', 'credit', 'void', ]

    GATEWAY_HOST = ["ws.firstdataglobalgateway.com",
                    "ws.merchanttest.firstdataglobalgateway.com"]
    GATEWAY_SERVICE = "/fdggwsapi/services"

    soap_env = "http://schemas.xmlsoap.org/soap/envelope/"
    fdggwsapi = "http://secure.linkpt.net/fdggwsapi/schemas_us/fdggwsapi"
    a1 = "http://secure.linkpt.net/fdggwsapi/schemas_us/a1"
    v1 = "http://secure.linkpt.net/fdggwsapi/schemas_us/v1"

    def __init__(self, username, password, pem_file='', key_file='', test=False):
        self.username = str(username)
        self.password = str(password)
        self.pem_file = pem_file or username + '.pem'
        self.key_file = key_file or username + '.key'
        self._arguments = {}
        self._test = test

    def process(self, **payment_arguments):
        self._arguments = payment_arguments
        url = 'https://%(host)s%(service)s' % {'host': self.GATEWAY_HOST[self._test],
                                               'service': self.GATEWAY_SERVICE}
        env = self.__init_env()
        order_request = SubElement(env[1], '{%s}FDGGWSApiOrderRequest' % self.fdggwsapi)
        self.__init_tree(order_request)

        text = tostring(env)

        try:
            r = requests.post(url=url,
                              data=text,
                              auth=(self.username, self.password),
                              cert=(self.pem_file, self.key_file))
        except Exception as ex:
            return {
                'TransactionTime': datetime.datetime.utcnow().strftime('%c'),
                'ErrorMessage': '{}'.format(ex),
                'OrderId': payment_arguments.get('OrderId', ''),
                'TransactionResult': 'S ERROR',
            }
        return self.__process_response(r)

    def __process_response(self, resp):
        response = parseString(resp.content)
        if response.getElementsByTagName('SOAP-ENV:Fault'):
            assert self._test, response.getElementsByTagName('detail')[0] \
                .firstChild.data.strip()
            return {
                'faultcode': response.getElementsByTagName('faultcode')[0]
                                     .firstChild.data.strip(),
                'faultstring': response.getElementsByTagName('faultstring')[0]
                                       .firstChild.data.strip(),
                'detail': response.getElementsByTagName('detail')[0]
                                  .firstChild.data.strip()}
        element = response.getElementsByTagName('fdggwsapi:FDGGWSApiOrderResponse')
        d = parse_xml(element[0].toxml())['fdggwsapi:FDGGWSApiOrderResponse']['meta']
        return {key.split(':')[1]: value for key, value in d.items()}

    def __recursive_tree(self, tree, parent):
        for item, value in tree:
            if value:
                el = SubElement(parent, '{%s}%s' % (self.v1, item))

                if isinstance(value, list):
                    self.__recursive_tree(value, el)
                elif isinstance(value, str) or isinstance(value, unicode):
                    el.text = value
                elif isinstance(value, int) or isinstance(value, float):
                    el.text = str(value)
                elif isinstance(value, Decimal):
                    el.text = str(float(value))
                elif value is None:
                    el.text = u''
                else:
                    raise RuntimeError('unknown variable format')

    def __init_env(self):
        env = Element('{%s}Envelope' % self.soap_env)
        SubElement(env, '{%s}Header' % self.soap_env)
        SubElement(env, '{%s}Body' % self.soap_env)
        return env

    def __init_tree(self, order_request):
        credit_card_tx_type = self._arguments.get('CreditCardTxType', {})
        credit_card_data = self._arguments.get('CreditCardData', {})
        credit_card_3d_secure = self._arguments.get('CreditCard3DSecure', {})
        payment = self._arguments.get('Payment', {})
        transaction_details = self._arguments.get('TransactionDetails', {})
        billing = self._arguments.get('Billing', {})
        shipping = self._arguments.get('Shipping', {})
        tree = [
            ('Transaction', [
                ('CreditCardTxType', [
                    ('Type', credit_card_tx_type.get('Type', ''))
                ]),
                ('CreditCardData', [
                    ('CardNumber', credit_card_data.get('CardNumber', '')),
                    ('ExpMonth', credit_card_data.get('ExpMonth', '')),
                    ('ExpYear', credit_card_data.get('ExpYear', '')),
                    ('CardCodeValue ', credit_card_data
                     .get('CardCodeValue', '')),
                    ('CardCodeIndicator', credit_card_data
                     .get('CardCodeIndicator', '')),
                    ('TrackData', credit_card_data.get('TrackData', '')),
                ]),
                ('CreditCard3DSecure', [
                    ('PayerSecurityLevel', credit_card_3d_secure
                     .get('PayerSecurityLevel', '')),
                    ('AuthenticationValue', credit_card_3d_secure
                     .get('AuthenticationValue', '')),
                    ('XID', credit_card_3d_secure.get('XID', '')),
                ]),
                ('Payment', [
                    ('ChargeTotal', payment.get('ChargeTotal', '')),
                    ('SubTotal', payment.get('XISubTotalD', '')),
                    ('VATTax', payment.get('VATTax', '')),
                    ('Shipping', payment.get('Shipping', '')),
                ]),
                ('TransactionDetails', [
                    ('UserID', transaction_details.get('UserID', '')),
                    ('InvoiceNumber', transaction_details
                     .get('InvoiceNumber', '')),
                    ('OrderId', transaction_details.get('OrderId', '')),
                    ('Ip', transaction_details.get('Ip', '')),
                    ('ReferenceNumber', transaction_details
                     .get('ReferenceNumber', '')),
                    ('TDate', transaction_details.get('TDate', '')),
                    ('Recurring', transaction_details.get('Recurring', 'No')),
                    ('TaxExempt', transaction_details.get('TaxExempt', '')),
                    ('TerminalType', transaction_details
                     .get('TerminalType', '')),
                    ('TransactionOrigin', transaction_details
                     .get('TransactionOrigin', '')),
                    ('PONumber', transaction_details.get('PONumber', '')),
                    ('DeviceID', transaction_details.get('DeviceID', '')),
                ]),
                ('Billing', [
                    ('CustomerID', billing.get('CustomerID', '')),
                    ('Name', billing.get('Name', '')),
                    ('Company', billing.get('Company', '')),
                    ('Address1', billing.get('Address1', '')),
                    ('Address2', billing.get('Address2', '')),
                    ('City', billing.get('City', '')),
                    ('State', billing.get('State', '')),
                    ('Zip', billing.get('Zip', '')),
                    ('Country', billing.get('Country', '')),
                    ('Phone', billing.get('Phone', '')),
                    ('Fax', billing.get('Fax', '')),
                    ('Email', billing.get('Email', '')),
                ]),
                ('Shipping', [
                    ('Type', shipping.get('Type', '')),
                    ('Name', shipping.get('Name', '')),
                    ('Company', shipping.get('Company', '')),
                    ('Address1', shipping.get('Address1', '')),
                    ('Address2', shipping.get('Address2', '')),
                    ('City', shipping.get('City', '')),
                    ('State', shipping.get('State', '')),
                    ('Zip', shipping.get('Zip', '')),
                    ('Country', shipping.get('Country', '')),
                ]),
            ])
        ]
        self.__recursive_tree(tree, order_request)

    def check(self):
        text = '' \
            '<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns' \
            ':SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-EN' \
            'V:Header /><SOAP-ENV:Body><fdggwsapi:FDGGWSApiActionRequest xm' \
            'lns:fdggwsapi="http://secure.linkpt.net/fdggwsapi/schemas_us/f' \
            'dggwsapi" xmlns:a1="http://secure.linkpt.net/fdggwsapi/schemas' \
            '_us/a1" xmlns:v1="http://secure.linkpt.net/fdggwsapi/schemas_u' \
            's/v1"><a1:Action><a1:SystemCheck/></a1:Action></fdggwsapi:FDGG' \
            'WSApiActionRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>'

        url = 'https://%(host)s%(service)s' % \
              {'host': self.GATEWAY_HOST[self._test],
               'service': self.GATEWAY_SERVICE}
        r = requests.post(url=url,
                          data=text,
                          auth=(self.username, self.password),
                          cert=(self.pem_file, self.key_file))
        return r.text


if __name__ == "__main__":
    from pprint import pprint

    lp = LinkPoint('WS1909530135._.1', 'UxdIsJVF',
                   key_file='WS1909530135._.2.key',
                   pem_file='WS1909530135._.1.pem', test=True)
    CreditCardData = {
        'CardNumber': '341134113411347',
        'ExpMonth': '04',
        'ExpYear': '16',
    }
    # pprint(lp.process(CreditCardTxType={'Type': 'sale'},
    #                   TransactionDetails={'PONumber': 'N000004', 'UserID': 'Kiosk1'},
    #                   CreditCardData=CreditCardData, Payment={'ChargeTotal': 6.00}))
    # pprint(lp.process(CreditCardTxType={'Type': 'preAuth'},
    #                   TransactionDetails={'PONumber': 'N000009', 'UserID': 'Kiosk1'},
    #                   CreditCardData=CreditCardData, Payment={'ChargeTotal': 0.02}))
    # pprint(lp.process(CreditCardTxType={'Type': 'postAuth'},
    #                   TransactionDetails={'OrderId': 'A-4a025d15-6aa3-4f2b-9974-d26a714384a4', 'UserID': 'Kiosk1'},
    #                   Payment={'ChargeTotal': 0.02}))
    # pprint(lp.process(CreditCardTxType={'Type': 'void'},
    #                   TransactionDetails={'OrderId': 'A-a52e54ad-bdee-4f4a-91cd-345b0aeb96f2', 'UserID': 'Kiosk1',
    #                                       'TDate': '1421153478'}))
    # pprint(lp.process(CreditCardTxType={'Type': 'return'},
    #                   TransactionDetails={'OrderId': 'A-a52e54ad-bdee-4f4a-91cd-345b0aeb96f2', 'UserID': 'Kiosk1'},
    #                   CreditCardData=CreditCardData, Payment={'ChargeTotal': 4.00}))
    # pprint(lp.process(CreditCardTxType={'Type': 'credit'},
    #                   CreditCardData=CreditCardData, Payment={'ChargeTotal': 4.00}))

    # print lp.check()