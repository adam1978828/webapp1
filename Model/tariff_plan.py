# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, object_session, validates
from tariff_value import TariffValue
from kiosk import Kiosk
from base import Base, ExtMixin
from libs.validators.core import validate_type_of, model_validator
from types import StringType
from django.core.validators import ValidationError
from sqlalchemy import or_

__author__ = 'D.Ivanets, D.Kalpakchi'


class TariffPlan(Base, ExtMixin):
    __tablename__ = u'c_tariff_plan'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    name = sa.Column('name', sa.String(255), default='')
    company_id = sa.Column('company_id', sa.Numeric, sa.ForeignKey('c_company.id'))
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    # price = sa.Column('price', sa.Numeric)
    # period = sa.Column('period', sa.Numeric)

    UniqueConstraint(company_id, name)

    company = relationship('Company')
    tariff_value = relationship('TariffValue', lazy='dynamic')
    user = relationship('User')

    sync_filter_rules = [lambda request: (TariffPlan.company == request.kiosk.company), ]

    @validates('name')
    @model_validator
    def check_name(self, key, value):
        if not value:
            raise ValidationError("Tariff plan name can't be empty")
        return value

    def __init__(self, name='', company=None, price=0):
        ExtMixin.__init__(self)
        self.name = name
        self.company = company
        self.price = price

    @sa.orm.reconstructor
    def init_on_load(self): 
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @hybrid_property
    def last_tariff_value(self):
        last_tariff = object_session(self).query(TariffValue)\
            .filter_by(tariff_plan_id=self.id)\
            .filter_by(kiosk_id=None)\
            .order_by(TariffValue.id.desc()).first()
        return last_tariff

    @hybrid_property
    def kiosk_with_custom_values(self):
        last_tariff = object_session(self).query(Kiosk)\
            .filter_by(tariff_plan_id=self.id)\
            .filter_by(kiosk_id=None)\
            .order_by(TariffValue.id.desc()).first()
        return last_tariff

    # @last_tariff_value.expression
    # def last_rate_plan(cls):
    # return
    # cls.query.filter_by(tariff_plan_id=cls.id).order_by(TariffValue.id.desc()).limit(1)
