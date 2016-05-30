from coupons.helpers.processor import CouponProcessor
from decimal import Decimal, localcontext, BasicContext

__author__ = 'D.Kalpakchi'


def calculate_rent(upc, kiosk, discount):
    """
    Calculates rental price for upc per particular kiosk.
    :param upc:
    :param kiosk:
    :param discount:
    :return:
    """

    settings = kiosk.settings
    actual_tariff = upc.get_tariff_value(kiosk)
    discount = discount or 0

    with localcontext(BasicContext):
        tax_rate = Decimal(str(settings.rent_tax_rate)) / Decimal('100.0')
        first_night_tariff = Decimal(str(actual_tariff.first_night))\
            .quantize(Decimal('0.01'))
        sub_total = first_night_tariff
        total_with_discount = (sub_total - Decimal(str(discount)))\
            .quantize(Decimal('0.01'))
        taxes = tax_rate * total_with_discount

    return sub_total, taxes, discount, total_with_discount + taxes


def expected_total_rent(data):
    """
    Calculates expected total amount for reserved rents.
    :param data:
    :return: list of tuples with prices for upc
    :rtype: list
    """

    return [tuple([float(sum(item)) for item in zip(*([(0, 0, 0, 0)] + [calculate_rent(upc, kiosk, discount) for upc, kiosk, available, discount in data if available]))]) if data else (0, 0, 0, 0)]