# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, class_mapper
from sqlalchemy.orm import validates

from base import Base, ExtMixin
from mixins.validate_settings import ValidateSettings


__author__ = 'D.Ivanets'


class KioskSettings(Base, ExtMixin, ValidateSettings):
    """
    """
    __tablename__ = u'c_kiosk_settings'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'), primary_key=True)
    alias = sa.Column('alias', sa.String(128), default='')
    timezone_id = sa.Column('timezone_id', sa.Numeric(3, 0), sa.ForeignKey('e_timezone.id'))
    currency_id = sa.Column('currency_id', sa.Numeric(3, 0), sa.ForeignKey('e_currency.id'))
    dvd_tariff_plan_id = sa.Column('dvd_tariff_plan_id', sa.Numeric(3, 0), sa.ForeignKey('c_tariff_plan.id'))
    blu_ray_tariff_plan_id = sa.Column('blu_ray_tariff_plan_id', sa.Numeric(3, 0), sa.ForeignKey('c_tariff_plan.id'))
    game_tariff_plan_id = sa.Column('game_tariff_plan_id', sa.Numeric(3, 0), sa.ForeignKey('c_tariff_plan.id'))
    company_payment_system_id = sa.Column('company_payment_system_id', sa.Numeric(3, 0),
                                          sa.ForeignKey('ps_company_payment_system.id'), default=None)
    speaker_volume = sa.Column('speaker_volume', sa.Numeric(3, 0), default=None)
    rent_tax_rate = sa.Column('rent_tax_rate', sa.Numeric(5, 3), default=None)
    sale_tax_rate = sa.Column('sale_tax_rate', sa.Numeric(5, 3), default=None)
    tax_jurisdiction = sa.Column('tax_jurisdiction', sa.String(64), default=None)
    reservation_expiration_period = sa.Column('reservation_expiration_period', sa.Numeric(4, 0), default=None)
    max_disks_per_card = sa.Column('max_disks_per_card', sa.Numeric(2, 0), default=None)
    grace_period = sa.Column('grace_period', sa.Numeric(3, 0), default=None)
    sale_convert_type = sa.Column('sale_convert_type', sa.Numeric(1, 0), default=None)
    sale_convert_days = sa.Column('sale_convert_days', sa.Numeric(5, 0), default=None)
    sale_convert_price = sa.Column('sale_convert_price', sa.Numeric(7, 2), default=None)
    dvd_preauth_method_id = sa.Column('dvd_preauth_method_id', sa.Numeric(1, 0), sa.ForeignKey('e_preauth_method.id'))
    blu_ray_preauth_method_id = sa.Column('blu_ray_preauth_method_id', sa.Numeric(1, 0),
                                          sa.ForeignKey('e_preauth_method.id'))
    game_preauth_method_id = sa.Column('game_preauth_method_id', sa.Numeric(1, 0), sa.ForeignKey('e_preauth_method.id'))
    dvd_preauth_amount = sa.Column('dvd_preauth_amount', sa.Numeric(7, 2), default=None)
    blu_ray_preauth_amount = sa.Column('blu_ray_preauth_amount', sa.Numeric(7, 2), default=None)
    game_preauth_amount = sa.Column('game_preauth_amount', sa.Numeric(7, 2), default=None)
    rent_no_internet_op_id = sa.Column('rent_no_internet_op_id', sa.Numeric(1, 0),
                                       sa.ForeignKey('e_no_internet_operation.id'))
    sale_no_internet_op_id = sa.Column('sale_no_internet_op_id', sa.Numeric(1, 0),
                                       sa.ForeignKey('e_no_internet_operation.id'))
    capture_retry_interval = sa.Column('capture_retry_interval', sa.Numeric(5, 0), default=None)
    capture_retry_quantity = sa.Column('capture_retry_quantity', sa.Numeric(3, 0), default=None)
    contact_telephone_number = sa.Column('contact_telephone_number', sa.String(20), default=None)
    terms = sa.Column('terms', sa.Text, default=None)
    password = sa.Column('pass', sa.String(128), default='root')
    is_bluray_warning = sa.Column('is_bluray_warning', sa.Boolean, default=None)
    is_smart_capture_retry = sa.Column('is_smart_capture_retry', sa.Boolean, default=None)
    empty_slots_warning = sa.Column('empty_slots_warning', sa.Numeric(3, 0), default=None)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    t_day_start = sa.Column('t_day_start', sa.Time, default=datetime.time(8, 0, 0))
    t_return = sa.Column('t_return', sa.Time, default=datetime.time(20, 0, 0))
    # name = sa.Column('name', sa.String(128), default='')

    kiosk = relationship('Kiosk')
    timezone = relationship('Timezone')
    currency = relationship('Currency')
    dvd_tariff_plan = relationship('TariffPlan', foreign_keys=dvd_tariff_plan_id)
    blu_ray_tariff_plan = relationship('TariffPlan', foreign_keys=blu_ray_tariff_plan_id)
    game_tariff_plan = relationship('TariffPlan', foreign_keys=game_tariff_plan_id)
    company_payment_system = relationship('CompanyPaymentSystem')
    dvd_preauth_method = relationship('PreauthMethod', foreign_keys=dvd_preauth_method_id)
    blu_ray_preauth_method = relationship('PreauthMethod', foreign_keys=blu_ray_preauth_method_id)
    game_preauth_method = relationship('PreauthMethod', foreign_keys=game_preauth_method_id)
    rent_no_internet_op = relationship('NoInternetOperation', foreign_keys=rent_no_internet_op_id)
    sale_no_internet_op = relationship('NoInternetOperation', foreign_keys=sale_no_internet_op_id)
    languages = relationship('Language', secondary='c_kiosk_settings_to_language')
    skip_dates = relationship('KioskSkipDates')
    skip_dates_alt = relationship('KioskSkipDates', lazy='dynamic')
    skip_weekdays = relationship('KioskSkipWeekdays')
    skip_weekdays_alt = relationship('KioskSkipWeekdays', lazy='dynamic')

    sync_filter_rules = [
        lambda request: (KioskSettings.id == request.kiosk.id),
    ]

    def __init__(self, kiosk=None):
        ExtMixin.__init__(self)
        self.kiosk = kiosk

    @sa.orm.reconstructor
    def init_on_load(self): 
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @hybrid_property
    def actual_skip_days(self):
        return self.skip_weekdays.filter_by(is_active=True)

    @hybrid_property
    def actual_skip_dates(self):
        return self.skip_dates.filter_by(is_active=True)

    def get_instance(self):
        d = {}
        for field in (col.key for col in class_mapper(type(self)).iterate_properties
                      if isinstance(col, sa.orm.ColumnProperty)):
            d[field] = self.__getattribute__(field)
            if field not in ('id', 'alias'):
                if d[field] is None:
                    d[field] = self.kiosk.company.company_settings.__getattribute__(field)
            if isinstance(d[field], datetime.datetime):
                d[field] = d[field].isoformat()
            # Handler: Decimal
            elif isinstance(d[field], Decimal):
                if d[field]._isinteger():
                    d[field] = int(d[field])
                else:
                    d[field] = float(d[field])
        # d['languages'] = self.languages or self.kiosk.company.company_settings.languages
        return d