# -*- coding: utf-8 -*-
import datetime
import uuid

from pytz import timezone
from dateutil import parser
from django.core.validators import ValidationError
import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates, object_session

from libs.validators.core import model_validator
from .base import Base, ExtMixin
from decimal import BasicContext, localcontext, Decimal

__author__ = 'D.Ivanets, D.Kalpakchi'


DEAL_STATUS_NOT_TO_SYNC = [
    101,  # "NEW RENT"
    102,  # "NEW SALE"
    201,  # "PREAUTH RENT"
    202,  # "PREAUTH SALE"
    211,  # "NA RENT"
    212,  # "NA SALE"
    231,  # "NEW RESERVATION"
]


class Deal(Base, ExtMixin):
    __tablename__ = u'c_deal'
    __table_args__ = {}
    id = sa.Column('id', sa.String(36), primary_key=True)
    card_id = sa.Column('card_id', sa.String(36), sa.ForeignKey('c_card.id'))
    coupon_id = sa.Column('coupon_id', sa.Numeric, sa.ForeignKey('d_coupon.id'))
    dt_start = sa.Column('dt_start', sa.DateTime)
    dt_end = sa.Column('dt_end', sa.DateTime)
    dt_rent_expire = sa.Column('dt_rent_expire', sa.DateTime)
    dt_reservation_expire = sa.Column('dt_reservation_expire', sa.DateTime)
    deal_type_id = sa.Column('deal_type_id', sa.Numeric(2, 0),
                             sa.ForeignKey('e_deal_type.id'))
    deal_status_id = sa.Column('deal_status_id', sa.Numeric(3, 0),
                               sa.ForeignKey('e_deal_status.id'),
                               default=0)
    tariff_value_id = sa.Column('tariff_value_id', sa.Numeric(10, 0),
                                sa.ForeignKey('c_tariff_values.id'))
    rf_id = sa.Column('rf_id', sa.String(18), sa.ForeignKey('disk.rf_id'))
    kiosk_start_id = sa.Column('kiosk_start_id', sa.Numeric(10, 0),
                               sa.ForeignKey('c_kiosk.id'))
    kiosk_end_id = sa.Column('kiosk_end_id', sa.Numeric(10, 0),
                             sa.ForeignKey('c_kiosk.id'))
    closed = sa.Column('closed', sa.Boolean, default=False)
    dt_modify = sa.Column('dt_modify', sa.DateTime,
                          default=datetime.datetime.utcnow,
                          onupdate=datetime.datetime.utcnow)
    preauth_amount = sa.Column('preauth_amount', sa.Numeric(7, 2), default=0)
    total_days = sa.Column('total_days', sa.Numeric(3, 0), default=0)
    dt_next_retry = sa.Column('dt_next_retry', sa.DateTime)

    # the amount to be withdrawn
    total_amount = sa.Column('total_amount', sa.Numeric(7, 2), default=0)
    force_total_amount = sa.Column('force_total_amount', sa.Boolean,
                                   default=False)
    discount = sa.Column('discount', sa.Numeric(7, 2), default=0)
    taxes = sa.Column('taxes', sa.Numeric(7, 2), default=0)
    tariff_charge = sa.Column('tariff_charge', sa.Numeric(7, 2), default=0)
    secret_code = sa.Column('secret_code', sa.String(8))

    company_payment_system_id = sa.Column(
        'company_payment_system_id', sa.Numeric(3, 0),
        sa.ForeignKey('ps_company_payment_system.id'), default=None)

    card = relationship('Card', backref='deals')
    coupon = relationship('Coupon', backref='deals')
    deal_type = relationship('DealType', backref='deals')
    deal_status = relationship('DealStatus', backref='deals')
    tariff_value = relationship('TariffValue', backref='deals')
    disk = relationship('Disk', backref='deals')
    kiosk_start = relationship('Kiosk', foreign_keys=kiosk_start_id)
    kiosk_end = relationship('Kiosk', foreign_keys=kiosk_end_id)
    linkpoint_transaction = relationship('LinkpointTransactions',
                                         order_by="LinkpointTransactions.id")
    linkpoint_transaction_lazy = relationship(
        'LinkpointTransactions', order_by="LinkpointTransactions.id",
        lazy='dynamic')
    firstdata_transaction_lazy = relationship(
        'FirstdataTransactions', order_by="FirstdataTransactions.id",
        lazy='dynamic')
    company = relationship("Company", secondary='c_card', uselist=False)
    user = relationship('User', secondary='c_card', uselist=False)
    payment_account = relationship('CompanyPaymentSystem')
    
    sync_filter_rules = [
        lambda request: (Deal.company == request.kiosk.company),
        lambda request: (Deal.deal_status_id.notin_(DEAL_STATUS_NOT_TO_SYNC)),
    ]

    def __init__(self, d_id=None):
        ExtMixin.__init__(self)
        if not d_id:
            self.id = uuid.uuid1().hex
        else:
            self.id = d_id

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    @model_validator
    @validates('dt_end')
    def check_dt_end(self, key, value):
        if value is not None:
            if isinstance(value, str) or isinstance(value, unicode):
                value = parser.parse(value)
            elif not isinstance(value, datetime.datetime):
                raise ValidationError('Wrong type of given data')

            if value < self.dt_start:
                raise ValidationError('End date can not be smaller than start date')
        return value

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @property
    def total_preauth(self):
        return self.payment_account.system.deal_total_preauth(self)

    @property
    # the amount which is already charged
    def total_charged(self):
        return self.payment_account.system.deal_total_charged(self)

    def count_rental_period(self, end_date=None):
        kiosk = self.kiosk_start
        kiosk_tz = kiosk.tz_info
        utc = timezone('UTC')
        started = utc.localize(self.dt_start) \
            .astimezone(kiosk_tz).replace(tzinfo=None)
        finished = end_date or self.dt_end or datetime.datetime.utcnow()
        finished = finished.replace(tzinfo=None)
        finished = utc.localize(finished) \
            .astimezone(kiosk_tz).replace(tzinfo=None)
        kiosk_day_start = self.kiosk_start.settings.t_day_start
        kiosk_day_end = self.kiosk_start.settings.t_return

        skipped_dates = []
        for date in kiosk.actual_skip_dates:
            if date.year:
                skipped_dates.append(date.date())
            else:
                skipped_dates.append(date.date(year=started.year))
                skipped_dates.append(date.date(year=finished.year))

        # Choose all skipped days for current kiosk
        skipped_days = [int(d.weekday) for d in kiosk.actual_skip_days]

        # the period disk was absent in kiosk
        days_charged = (finished.date() - started.date()).days

        # days from start to end without that +/- days
        charged = [(started + datetime.timedelta(days=x)).date() for x in xrange(0, days_charged)]

        # filter out skipped weekdays
        charged = [d for d in charged if d.weekday() + 1 not in skipped_days]

        # filter out skipped dates
        charged = [d for d in charged if d not in skipped_dates]

        days_charged = len(charged)
        # Indeed there are two variants:
        # => if time started is less than kiosk day start
        # => if time finished is greater than kiosk day end
        if started.time() <= kiosk_day_start:
            days_charged += 1
        if finished.time() >= kiosk_day_end:
            days_charged += 1

        days_charged = days_charged or 1

        return days_charged

    def count_dt_expire(self):
        """Counts datetime, after which deal will be converted to sale.
        :return: datetime.datetime, final expiration datetime
        """
        settings = self.kiosk_start.settings

        if settings.sale_convert_type == 1:
            # Days
            max_days = int(settings.sale_convert_days)
        else:
            # 'Dollars'
            tv = self.tariff_value
            max_amount = int(settings.sale_convert_price)
            fn_value = self.get_first_night()
            max_days = int((max_amount - fn_value) / tv.next_night + 1)
        end_time = settings.t_return
        end_date = self.dt_start.date() + datetime.timedelta(days=max_days)
        end_datetime = datetime.datetime.combine(end_date, end_time) - \
                       datetime.timedelta(seconds=1)
        end_datetime = timezone(settings.timezone.name).localize(end_datetime) \
            .astimezone(timezone('UTC')).replace(tzinfo=None)
        while self.count_rental_period(
                        end_datetime + datetime.timedelta(days=1)) <= max_days:
            end_datetime += datetime.timedelta(days=1)
        return end_datetime

    def calculate_amount(self):
        """
        Calculate total amount for deal.
        :return:
        """
        settings = self.kiosk_start.settings

        if self.deal_type_id == 1:
            # Rent
            # Use localcontext(BasicContext) for proper rounding of decimal
            # numbers
            with localcontext(BasicContext):

                tax_rate = settings.rent_tax_rate / Decimal('100.0')

                max_total = self.kiosk_start.settings.sale_convert_price

                # First night value
                fn_val = self.get_first_night()
                # Next night value
                fn_val = Decimal(fn_val)
                nn_val = Decimal(self.tariff_value.next_night)

                days_rent = Decimal(self.total_days) - 1

                sub_total = fn_val + days_rent * nn_val

                sub_total_with_discount = sub_total - self.discount

                if sub_total_with_discount > max_total:
                    total = max_total
                    taxes = tax_rate * max_total
                else:
                    total = sub_total_with_discount
                    taxes = tax_rate * sub_total_with_discount

                self.tariff_charge = total.quantize(Decimal('0.01'))

                self.taxes = taxes.quantize(Decimal('0.01'))

                total_charge = self.tariff_charge + self.taxes
                total_charge = float(total_charge)

            return total_charge

        elif self.deal_type_id == 2:
            # Sale
            with localcontext(BasicContext):
                tax_rate = Decimal(settings.sale_tax_rate) / Decimal('100.0')

                sale_tariff = Decimal(self.tariff_value.sale)

                self.taxes = (tax_rate * sale_tariff).quantize(Decimal('0.01'))

                total = (sale_tariff + self.taxes).quantize(Decimal('0.01'))

            return float(total)
        else:
            # OverRent
            return -1

    def get_preauth_amount(self):
        # TODO: cleanup this function, check all Decimal calculations.
        # amount = Decimal(0)
        amount = 0.
        kiosk = self.kiosk_start
        t_v = self.tariff_value
        k_s = kiosk.settings
        c_s = kiosk.company.company_settings
        # Choose preauth amount for rent
        if self.deal_type_id == 1:
            # Preauth amount for DVD
            if self.disk.upc.format.id == 1:
                dvd_preauth_method = k_s.dvd_preauth_method.id or \
                                     c_s.dvd_preauth_method.id
                method_value = [None, 0,
                                self.get_first_night(),
                                t_v.sale,
                                k_s.dvd_preauth_amount]

                amount += float(method_value[int(dvd_preauth_method)])
            # Preauth amount for Blu-ray
            elif self.disk.upc.format.id == 2:
                br_preauth_method = k_s.blu_ray_preauth_method.id or \
                                    c_s.blu_ray_preauth_method.id
                method_value = [None, 0,
                                self.get_first_night(),
                                t_v.sale,
                                k_s.blu_ray_preauth_amount]

                amount += float(method_value[int(br_preauth_method)])
            else:
                raise RuntimeError(u'Wrong value: %s' % self.disk.upc.format.id)

            amount *= 1 + float(k_s.rent_tax_rate)/100.

        # Preauth amount for purchase
        elif self.deal_type_id == 2:
            amount += float(t_v.sale)
            amount *= 1 + float(k_s.sale_tax_rate) / 100.
        else:
            raise RuntimeError(u'incorrect deal_type_id value: %s'
                               % self.deal_type_id)

        # Proper rounding of float
        with localcontext(BasicContext):
            amount = Decimal(str(amount))
            amount = amount.quantize(Decimal('0.01'))
        # print '===================================================', amount
        return float(amount)

    @property
    def payment_system(self):
        if not self.payment_account:
            self.payment_account = self.kiosk_start.payment_system
        return self.payment_account.system

    def ps_preauth(self):
        self.payment_system.preauth_deal(self)

    def rm_coupon(self):
        self.coupon = None
        self.coupon_id = None
        self.discount = 0

    # def ps_process_amount(self):
    def start_weekday(self):
        if not self.kiosk_start:
            return
        kiosk_tz = self.kiosk_start.tz_info
        utc = timezone('UTC')
        started = utc.localize(self.dt_start) \
            .astimezone(kiosk_tz).replace(tzinfo=None)
        return started.weekday()

    def get_first_night(self):
        return self.tariff_value.get_first_night(self.start_weekday())

    def is_fully_charged(self):
        charged = round(float(self.total_charged), 2)
        total = round(float(self.total_amount), 2)
        return charged == total
