# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session

from .base import Base, ExtMixin
from mixins.validate_settings import ValidateSettings


__author__ = 'D.Ivanets, D.Kalpakchi'


class CompanySettings(Base, ExtMixin, ValidateSettings):
    __tablename__ = u'c_company_settings'
    __table_args__ = {}

    id = sa.Column('id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'), primary_key=True)
    timezone_id = sa.Column('timezone_id', sa.Numeric(3, 0), sa.ForeignKey('e_timezone.id'))
    currency_id = sa.Column('currency_id', sa.Numeric(3, 0), sa.ForeignKey('e_currency.id'))
    dvd_tariff_plan_id = sa.Column('dvd_tariff_plan_id', sa.Numeric(3, 0), sa.ForeignKey('c_tariff_plan.id'))
    blu_ray_tariff_plan_id = sa.Column('blu_ray_tariff_plan_id', sa.Numeric(3, 0), sa.ForeignKey('c_tariff_plan.id'))
    game_tariff_plan_id = sa.Column('game_tariff_plan_id', sa.Numeric(3, 0), sa.ForeignKey('c_tariff_plan.id'))
    company_payment_system_id = sa.Column('company_payment_system_id', sa.Numeric(3, 0),
                                          sa.ForeignKey('ps_company_payment_system.id'))
    speaker_volume = sa.Column('speaker_volume', sa.Numeric(3, 0), default=100)
    rent_tax_rate = sa.Column('rent_tax_rate', sa.Numeric(5, 3), default=0)
    sale_tax_rate = sa.Column('sale_tax_rate', sa.Numeric(5, 3), default=0)
    tax_jurisdiction = sa.Column('tax_jurisdiction', sa.String(64), default='')
    reservation_expiration_period = sa.Column('reservation_expiration_period', sa.Numeric(4, 0), default=60)
    max_disks_per_card = sa.Column('max_disks_per_card', sa.Numeric(2, 0), default=5)
    grace_period = sa.Column('grace_period', sa.Numeric(3, 0), default=15)
    sale_convert_type = sa.Column('sale_convert_type', sa.Numeric(1, 0), default=0)
    sale_convert_days = sa.Column('sale_convert_days', sa.Numeric(5, 0), default=10)
    sale_convert_price = sa.Column('sale_convert_price', sa.Numeric(7, 2), default=20)
    dvd_preauth_method_id = sa.Column('dvd_preauth_method_id', sa.Numeric(1, 0), sa.ForeignKey('e_preauth_method.id'))
    blu_ray_preauth_method_id = sa.Column('blu_ray_preauth_method_id', sa.Numeric(1, 0),
                                          sa.ForeignKey('e_preauth_method.id'))
    game_preauth_method_id = sa.Column('game_preauth_method_id', sa.Numeric(1, 0), sa.ForeignKey('e_preauth_method.id'))
    dvd_preauth_amount = sa.Column('dvd_preauth_amount', sa.Numeric(7, 2), default=4)
    blu_ray_preauth_amount = sa.Column('blu_ray_preauth_amount', sa.Numeric(7, 2), default=6)
    game_preauth_amount = sa.Column('game_preauth_amount', sa.Numeric(7, 2), default=6)
    rent_no_internet_op_id = sa.Column('rent_no_internet_op_id', sa.Numeric(1, 0),
                                       sa.ForeignKey('e_no_internet_operation.id'))
    sale_no_internet_op_id = sa.Column('sale_no_internet_op_id', sa.Numeric(1, 0),
                                       sa.ForeignKey('e_no_internet_operation.id'))
    capture_retry_interval = sa.Column('capture_retry_interval', sa.Numeric(5, 0), default=300)
    capture_retry_quantity = sa.Column('capture_retry_quantity', sa.Numeric(3, 0), default=0)
    contact_telephone_number = sa.Column('contact_telephone_number', sa.String(20), default='')
    terms = sa.Column('terms', sa.Text, default='')
    is_bluray_warning = sa.Column('is_bluray_warning', sa.Boolean, default=False)
    is_smart_capture_retry = sa.Column('is_smart_capture_retry', sa.Boolean, default=False)
    empty_slots_warning = sa.Column('empty_slots_warning', sa.Numeric(3, 0), default=30)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow)
    t_day_start = sa.Column('t_day_start', sa.Time, default=datetime.time(8, 0, 0))
    t_return = sa.Column('t_return', sa.Time, default=datetime.time(20, 0, 0))
    # name = sa.Column('name', sa.String(128), default='')

    company = relationship('Company')
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
    languages = relationship('Language', secondary='c_company_settings_to_language')
    skip_dates = relationship('CompanySkipDates')
    skip_weekdays = relationship('CompanySkipWeekdays')
    # user = relationship('User')

    def __init__(self, company=None):
        ExtMixin.__init__(self)
        if company:
            self.company = company

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()