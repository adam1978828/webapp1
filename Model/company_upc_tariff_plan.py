# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates

from libs.validators.string_validators import validate_string_not_empty
from libs.validators.core import model_validator
from .base import Base, ExtMixin


__author__ = 'D.Ivanets'


class CompanyUpcTariffPlan(Base, ExtMixin):
    __tablename__ = u'c_company_upc_tariff_plan'
    __table_args__ = {}
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'), primary_key=True)
    upc_link = sa.Column('upc_link', sa.String(20), sa.ForeignKey('upc.upc'), primary_key=True)
    tariff_plan_id = sa.Column('tariff_plan_id', sa.Numeric(10, 0), sa.ForeignKey('c_tariff_plan.id'))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    company = relationship('Company')
    upc = relationship('UPC')
    tariff_plan = relationship('TariffPlan')

    sync_filter_rules = [lambda request: (CompanyUpcTariffPlan.company == request.kiosk.company), ]

    @validates('upc_link', 'tariff_plan_id', 'company_id')
    @model_validator
    def check_fields(self, key, value):
        validate_string_not_empty(value)
        return value

    def __init__(self):
        ExtMixin.__init__(self)

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s:%s:%s)>" % (self.__class__.__name__, self.company_id, self.upc_link, self.tariff_plan_id,)

    def __unicode__(self):
        return self.__repr__()
