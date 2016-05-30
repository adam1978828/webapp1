# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates
from base import Base, ExtMixin
from libs.validators.core import model_validator, validate_type_of, validate_range_of
from django.core.validators import ValidationError

__author__ = 'D.Ivanets, D.Kalpakchi'


class TariffValue(Base, ExtMixin):
    __tablename__ = u'c_tariff_values'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    tariff_plan_id = sa.Column('tariff_plan_id', sa.Numeric,
                               sa.ForeignKey('c_tariff_plan.id'))
    first_night = sa.Column('first_night', sa.Float(2))
    next_night = sa.Column('next_night', sa.Float(2))
    sale = sa.Column('sale', sa.Float(2))
    mon_night = sa.Column('mon_night', sa.Numeric(7, 2), default=None)
    tue_night = sa.Column('tue_night', sa.Numeric(7, 2), default=None)
    wed_night = sa.Column('wed_night', sa.Numeric(7, 2), default=None)
    thu_night = sa.Column('thu_night', sa.Numeric(7, 2), default=None)
    fri_night = sa.Column('fri_night', sa.Numeric(7, 2), default=None)
    sat_night = sa.Column('sat_night', sa.Numeric(7, 2), default=None)
    sun_night = sa.Column('sun_night', sa.Numeric(7, 2), default=None)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0),
                         sa.ForeignKey('c_kiosk.id'))
    dt_start = sa.Column('dt_start', sa.DateTime,
                         default=datetime.datetime.utcnow)
    dt_end = sa.Column('dt_end', sa.DateTime)
    dt_modify = sa.Column('dt_modify', sa.DateTime,
                          default=datetime.datetime.utcnow,
                          onupdate=datetime.datetime.utcnow)

    tariff_plan = relationship('TariffPlan')
    user = relationship('User')
    kiosk = relationship('Kiosk')
    company = relationship('Company', secondary='c_tariff_plan', uselist=False)

    sync_filter_rules = [
        lambda request: (TariffValue.company == request.kiosk.company),
    ]

    @validates('first_night')
    @model_validator
    def check_first_night(self, key, value):
        try:
            val = float(value)
            validate_range_of(val, min_value=0)
            return val
        except ValueError:
            if not value:
                msg = "First night tariff value can't be empty"
                raise ValidationError(msg)
            else:
                msg = "First night tariff value is not numeric. " \
                      "Give number, please"
                raise ValidationError(msg)
        except Exception, e:
            raise ValidationError(e.message)

    @validates('next_night')
    @model_validator
    def check_next_night(self, key, value):
        try:
            val = float(value)
            validate_range_of(val, min_value=0)
            return val
        except ValueError:
            if not value:
                msg = "Next night tariff value can't be empty"
                raise ValidationError(msg)
            else:
                msg = "Next night tariff value is not numeric. " \
                      "Give number, please"
                raise ValidationError(msg)
        except Exception, e:
            raise ValidationError(e.message)

    @validates('sale')
    @model_validator
    def check_sale(self, key, value):
        try:
            val = float(value)
            validate_range_of(val, min_value=0)
            return val
        except ValueError:
            if not value:
                msg = "Sale tariff value can't be empty"
                raise ValidationError(msg)
            else:
                msg = "Sale tariff value is not numeric. Give number, please"
                raise ValidationError(msg)
        except Exception, e:
            raise ValidationError(e.message)


    @validates('sun_night', 'mon_night', 'tue_night', 'wed_night', 'thu_night', 'fri_night', 'sat_night', )
    @model_validator
    def check_week_night(self, key, value):
        try:
            if value:
                val = float(value)
                validate_range_of(val, min_value=0, max_value=9999)
            else:
                val = None
            return val
        except ValueError:
            if value:
                raise ValidationError("This value is not numeric. Give number, please")
        except Exception, e:
            raise ValidationError(e.message)

    def __init__(self, tariff_plan=None, kiosk=None):
        ExtMixin.__init__(self)
        self.first_night = 1
        self.next_night = 1
        self.sale = 20
        if tariff_plan:
            self.tariff_plan = tariff_plan
        if kiosk:
            self.kiosk_id = kiosk.id

    @sa.orm.reconstructor
    def init_on_load(self): 
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s: $%s/%s/%s |%s|)>" % \
               (self.__class__.__name__, self.id, self.first_night,
                self.next_night, self.sale, self.kiosk_id)

    def __unicode__(self):
        return self.__repr__()

    def equal_by_values(self, tariff_value):
        return self.first_night == tariff_value.first_night and \
               self.next_night == tariff_value.next_night and \
               self.sale == tariff_value.sale

    def get_first_night(self, weekday=None):
        """
        :param weekday: Number of weekday. 0 - Monday ... 6 - Sunday
        :type weekday: int
        :return: First Night price for requested weekday.
        """
        if weekday is None:
            return self.first_night
        t_v = [
            self.mon_night, self.tue_night, self.wed_night, self.thu_night,
            self.fri_night, self.sat_night, self.sun_night
        ]
        t_v = [val if val is not None else self.first_night for val in t_v]
        return float(t_v[weekday])
