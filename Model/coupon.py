# -*- coding: utf-8 -*-
import datetime, pickle

import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates, object_session
from sqlalchemy.ext.hybrid import hybrid_property

from django.core.validators import ValidationError

from libs.validators.core import validate_numericality_of, validate_length_of, validate_integer_1_to_100
from libs.validators.core import validate_less_than, validate_float_0_to_1
from libs.validators.core import model_validator, validate_integer_gt_zero, validate_float_gt_zero
from libs.validators.string_validators import validate_string_not_empty

from .base import Base, ExtMixin
from deal import Deal

__author__ = 'D.Kalpakchi'


class Coupon(Base, ExtMixin):
    """
    Coupon class
    params: saved as pickled tuple
    """
    __tablename__ = u'd_coupon'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric, primary_key=True)
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'))
    coupon_type_id = sa.Column('coupon_type_id', sa.Numeric, sa.ForeignKey('e_coupon_type.id'))
    params = sa.Column('params', sa.String(50))
    usage_amount = sa.Column('usage_amount', sa.Numeric, nullable=False)
    code = sa.Column('code', sa.String(10), nullable=False)
    dt_create = sa.Column('dt_create', sa.DateTime, default=datetime.datetime.utcnow)
    dt_start = sa.Column('dt_start', sa.DateTime)
    dt_end = sa.Column('dt_end', sa.DateTime)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    used_total = sa.Column('used_total', sa.Numeric(10, 0), default=0)
    per_card_usage = sa.Column('per_card_usage', sa.Numeric(10, 0), default=0)

    main_coupon_id = sa.Column('main_coupon_id', sa.Numeric(10, 0), sa.ForeignKey('d_coupon.id'))
    modified_by_id = sa.Column('modified_by_id', sa.String(36), sa.ForeignKey('c_user.id'))
    is_deleted = sa.Column('is_deleted', sa.Boolean, default=False)

    type = relationship('CouponType', backref='coupons')
    company = relationship('Company')
    coupon_usage_info = relationship("CouponUsageInfo", lazy='dynamic')
    modified_by = relationship('User')

    sync_filter_rules = [lambda request: (Coupon.company == request.kiosk.company), ]

    def __init__(self, company_id, coupon_type_id, params, usage_amount, code, per_card_usage):
        ExtMixin.__init__(self)
        self.coupon_type_id = coupon_type_id
        self.company_id = company_id
        self.params = params
        self.usage_amount = usage_amount
        self.code = code
        self.per_card_usage = per_card_usage

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    @validates('coupon_type_id')
    @model_validator
    def check_pattern_id(self, key, value):
        validate_string_not_empty(value)
        return value

    @validates('dt_end')
    @model_validator
    def check_dt_end(self, key, value):
        if value <= (self.dt_start or self.dt_create):
            raise ValidationError("Finish date must be later than the start date")
        return value

    @validates('usage_amount')
    @model_validator
    def check_usage_amount(self, key, value):
        validate_string_not_empty(value)
        validate_numericality_of(value)
        return value

    @validates('per_card_usage')
    @model_validator
    def check_per_card_usage(self, key, value):
        validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_less_than(value, self.usage_amount)
        return value

    @validates('code')
    @model_validator
    def check_code(self, key, value):
        validate_string_not_empty(value)
        validate_length_of(value, max_value=10)
        return value

    @validates('params')
    @model_validator
    def check_params(self, key, params):
        # TODO: Change this validator name to validate_not_empty
        value = params
        count_val = ["First", "Second"]
        pattern_id = self.coupon_type_id
        if pattern_id == 2:# First Night % Off
            validate_float_0_to_1('This', value)
        if pattern_id == 4:# Rent n Disks, Get n Free
            validate_integer_gt_zero(count_val[0], value[0])
            validate_integer_gt_zero(count_val[1], value[1])
        if pattern_id == 5:# Rent n Disks, Get % Off
            validate_integer_gt_zero(count_val[0], value[0])
            validate_float_0_to_1(count_val[1], value[1])
        if pattern_id == 6:# $n.nn Off
            validate_float_gt_zero("This", value)
        value = params
        if value is not None:
            validate_string_not_empty(value)
            if isinstance(value, list):
                for num, item in enumerate(value):
                    validate_string_not_empty(item)
                    validate_numericality_of(item)
                    value[num] = float(item)
            else:
                validate_numericality_of(value)
                value = float(value)
            return pickle.dumps(value)
        else:
            # no params needed
            return pickle.dumps('')

    @hybrid_property
    def formula(self):
        params = pickle.loads(self.params)
        if isinstance(params, tuple) or isinstance(params, list):
            return self.type.decoded_pattern.format(*params)
        else:
            return self.type.decoded_pattern.format(params)

    @property
    def is_active(self):
        if self.is_deleted:
            return False
        if self.usage_amount <= self.used_total:
            return False
        time_now = datetime.datetime.utcnow()
        dt_start, dt_end = self.dt_start, self.dt_end
        if dt_start and dt_end:
            return dt_start <= time_now <= dt_end
        elif dt_start:
            return time_now >= dt_start
        elif dt_end:
            return dt_start <= dt_end
        else:
            return True

    def deactivate(self):
        self.code = unicode(self.code[:1]) + u'\"~\"' + unicode(self.code[1:])
        self.is_deleted = True

    def restore(self):
        self.code = self.code.replace(u'\"~\"', '')
        self.is_deleted = False

    def refresh_total_usage(self):
        accepted_status_list = (
            201, 301, 311, 511, 601, 521, 621, 701, 321, 231, 241)
        if object_session(self):
            value = object_session(self).query(Deal)\
                .filter(Deal.coupon == self)\
                .filter(Deal.deal_status_id.in_(accepted_status_list))\
                .count()
        else:
            value = 0
        self.used_total = value

    @property
    def actual_used_total(self):
        self.refresh_total_usage()
        return self.used_total
