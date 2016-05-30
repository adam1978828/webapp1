__author__ = 'denis'


def print_transaction_result(result):
    if result.get('transaction_approved', False):
        print '\033[92m'
    else:
        print '\033[91m'
    print '/\\' * 35, '\n', '=' * 70, '\n'
    for k in sorted(result.keys()):
        if k != 'ctr' and result[k] is not None:
            print k.rjust(20, ' '), ":", result[k]
    print result.get('ctr', '')
    print '\n', '=' * 70, '\n', 'V' * 70, '\n'
    print '\033[0m'


class PaymentOperationException(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidCreditCardNumber(PaymentOperationException):

    """
    Means, that cc number is incorrect and doesn't pass control symbol test
    """

    def __init__(self, number=''):
        # Call the base class constructor with the parameters it needs
        PaymentOperationException.__init__(
            self, "Credit card number '%s' in not valid" % number)


class InvalidExpiryDate(PaymentOperationException):

    def __init__(self, date=''):
        # Call the base class constructor with the parameters it needs
        PaymentOperationException.__init__(
            self, "Credit card expiration date '%s' in not valid" % date)


class InvalidAmount(PaymentOperationException):

    def __init__(self, amount=''):
        # Call the base class constructor with the parameters it needs
        PaymentOperationException.__init__(
            self, "Invalid Amount '%s'" % amount)


class InvalidCardHolder(PaymentOperationException):

    def __init__(self, name=''):
        # Call the base class constructor with the parameters it needs
        PaymentOperationException.__init__(
            self, "Credit card holder's '%s' in not valid" % name)


class InvalidAuthorizationNumber(PaymentOperationException):

    def __init__(self):
        # Call the base class constructor with the parameters it needs
        PaymentOperationException.__init__(
            self, "Invalid Authorization Number")


class InvalidRefund(PaymentOperationException):

    def __init__(self):
        # Call the base class constructor with the parameters it needs
        PaymentOperationException.__init__(self, "Invalid Refund")


class InvalidTransactionTag(PaymentOperationException):

    def __init__(self):
        # Call the base class constructor with the parameters it needs
        PaymentOperationException.__init__(self, "Invalid Transaction Tag")


class POUnknownError(PaymentOperationException):

    def __init__(self, message=''):
        # Call the base class constructor with the parameters it needs
        f = open('new_errors.txt', 'a')
        f.write(message + '\n')
        f.close()
        PaymentOperationException.__init__(
            self, "Unknown PO exception: %s" % message)


def p_error_check(result):
    import time
    time.sleep(1)
    bank_message = result.get('bank_message', '')
    print_transaction_result(result)
    if result.get('transaction_approved', False):
        return
    elif bank_message == 'Bad Request (22) - Invalid Credit Card Number':
        raise InvalidCreditCardNumber
    elif bank_message == 'Bad Request (25) - Invalid Expiry Date':
        raise InvalidExpiryDate
    elif bank_message == 'Invalid Expiration Date':
        raise InvalidExpiryDate(result.get('cc_expiry', ''))
    elif bank_message == 'Bad Request (26) - Invalid Amount':
        raise InvalidAmount(result.get('amount', ''))
    elif bank_message == 'Bad Request (27) - Invalid Card Holder':
        raise InvalidCardHolder
    elif bank_message == 'Bad Request (28) - Invalid Authorization Number':
        raise InvalidAuthorizationNumber
    elif bank_message == 'Bad Request (64) - Invalid Refund':
        raise InvalidRefund
    elif bank_message == 'Bad Request (69) - Invalid Transaction Tag':
        raise InvalidAuthorizationNumber

    else:
        raise POUnknownError(bank_message)
