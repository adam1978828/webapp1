import datetime
from libs.utils.list_functions import partition

DISK_THRESHOLD = 'disk_threshold'
DISK_APPLIED = 'disk_applied'
PRECISION = 2
OPERATION = 'operation'
VALUE = 'value'
DISCOUNT_VALUE = 0

PROPERTIES = {'n': 'next_night', 'e': 'entire_deal', 'f': 'first_night'}

class CouponProcessor(object):
    """
    Processor of coupons discounts

    To initialize processor, one must supply it with one obligatory argument:
    the instance of Coupon class.

    The optional argument is the set of rules about discounts.
    in the following format: {'first_night': True, 'next_night': False, 'entire_deal': True}
    'first_night' stands for first night discount
    'next_night' stands for next night discount
    'entire_deal' stands for entire deal discount

    The default value is: {'first_night': True, 'next_night': False, 'entire_deal': True} which is suitable for reservations
    processing. For deals processing, probably, it should be {'first_night': True, 'next_night': True, 'entire_deal': True}.

    Eventually, to compute discounts for cart or for one set of disk rentals, you need to do the following:
    cp = CouponProcessor(coupon)
    cp.discount(deals) # for deals
    cp.expected_discount(reservations) # for reservations
    Deals and reservations here are lists of appropriate objects, concerned with one cart or one set of
    user reservations.
    """

    def __init__(self, coupon, rules={'first_night': True,
                                      'next_night': False,
                                      'entire_deal': True}):
        self.discount_settings = {}
        self.disk_settings = {}
        self.coupon = coupon
        self.rules = rules
        self.card = None
        self.parse_pattern(coupon.formula)

    def parse_pattern(self, string):
        """
        :param string: e$0.011 ; 2.0:e0.5
        :return:
        """
        # print string
        if ':' in string:
            disk_off, money_off = string.split(':')
            if disk_off:
                self._parse_disk_off(disk_off)
            if money_off:
                self._parse_money_off(money_off)

        else:
            money_off = string
            self._parse_money_off(money_off)

    def _parse_disk_off(self, disk_off):
        disk_threshold, disk_applied = (map(float, disk_off.split('/')) + [None])[:2]
        self.disk_settings[DISK_THRESHOLD] = int(disk_threshold) if isinstance(disk_threshold, float) else disk_threshold
        self.disk_settings[DISK_APPLIED] = int(disk_applied) if isinstance(disk_applied, float) else disk_applied

    def _parse_money_off(self, money_off):
        map(self.parse_property_data, money_off.split(';'))

    def parse_property_data(self, property_data):
        property_alias = property_data[0]
        if property_alias in PROPERTIES:
            detailed_data = property_data.split('$')
            if len(detailed_data) > 1:
                key, value = detailed_data[0], float(detailed_data[1])
                property_fullname = PROPERTIES[key]
                operation = None
            else:
                property_fullname, value = PROPERTIES[property_alias], float(property_data[1:])
                operation = "__mul__"
            self.discount_settings[property_fullname] = dict({VALUE: value,
                                                              OPERATION: operation})

    def apply_discount(self, deal):
        amount, discount = deal.tariff_value.get_first_night(), DISCOUNT_VALUE
        for property_name, settings in self.discount_settings.iteritems():
            if self.rules[property_name]:
                operation = settings[OPERATION]
                value = settings[VALUE]
                discount += getattr(amount, operation)(value) if operation else value
        deal.discount = min(amount, round(discount, PRECISION))
        deal.coupon = self.coupon

    def expect_discount(self, reservation):
        if isinstance(reservation, dict):
            is_dict = True
            kiosk = reservation['kiosk']
            upc = reservation['upc']
        else:
            is_dict = False
            kiosk = reservation.kiosk
            upc = reservation.upc
        weekday = datetime.datetime.now(kiosk.tz_info).weekday()
        amount = upc \
            .get_tariff_value(kiosk) \
            .get_first_night(weekday)
        discount = 0
        for property_name, settings in self.discount_settings.iteritems():
            if self.rules[property_name]:
                operation = settings[OPERATION]
                value = settings[VALUE]
                discount += getattr(amount, operation)(value) if operation else value
        discount = min(amount, round(discount, 2))
        if is_dict:
            reservation['discount'] = discount
        else:
            reservation.discount = discount

    def expected_discount(self, reservations):
        if not reservations:
            return
        if isinstance(reservations[0], dict):
            is_dict = True
            key = lambda x: x['upc'].get_tariff_value(x['kiosk']).first_night
        else:
            is_dict = False
            key = lambda x: x.upc.get_tariff_value(x.kiosk).first_night
        reservations = sorted(reservations, key=key, reverse=True)
        if is_dict:
            for r in reservations:
                r['discount'] = 0
        else:
            for r in reservations:
                r.discount = 0
        disk_threshold = self.disk_settings.get(DISK_THRESHOLD, None)
        if disk_threshold is not None:
            reservations = partition(reservations, disk_threshold)
            for group in reservations:
                group.reverse()
                if len(group) == disk_threshold:
                    for reservation in group[:disk_threshold]:
                        self.expect_discount(reservation)
        else:
            for reservation in reservations:
                self.expect_discount(reservation)

    def discount(self, deals):
        deals = sorted(deals,
                       key=lambda x: x.tariff_value.get_first_night(),
                       reverse=True)
        [deal.rm_coupon() for deal in deals]

        if self.disk_settings:
            disk_threshold = self.disk_settings[DISK_THRESHOLD]
            disk_applied = self.disk_settings[DISK_APPLIED]
            deals = partition(deals, disk_threshold)
            for group in deals:
                group.reverse()
                if len(group) == disk_threshold:
                    for deal in group[:disk_applied]:
                        self.apply_discount(deal)
        else:
            for deal in deals:
                self.apply_discount(deal)

    def __str__(self):
        return str(self.__dict__)