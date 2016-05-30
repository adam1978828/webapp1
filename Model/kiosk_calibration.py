# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates
from libs.validators.core import model_validator, validate_float_gt_or_eq_zero, validate_numeric
from django.core.validators import ValidationError
from base import Base, ExtMixin


__author__ = 'D.Ivanets'


class KioskCalibration(Base, ExtMixin):
    """ Store kiosk calibration information
    """
    __tablename__ = u'c_kiosk_calibration'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'),
                   primary_key=True)
    alias = sa.Column('alias', sa.String(128), default='')

    top_offset = sa.Column('top_offset', sa.Numeric(8, 3), default=None)
    bottom_offset = sa.Column('bottom_offset', sa.Numeric(8, 3), default=None)
    exchange_offset = sa.Column('exchange_offset', sa.Numeric(8, 3),
                                default=None)
    back_offset = sa.Column('back_offset', sa.Numeric(8, 3), default=None)
    pulses_per_slot = sa.Column('pulses_per_slot', sa.Numeric(8, 3),
                                default=None)
    distance1 = sa.Column('distance1', sa.Numeric(8, 3), default=None)
    distance2 = sa.Column('distance2', sa.Numeric(8, 3), default=None)
    retry = sa.Column('retry', sa.Numeric(8, 3), default=None)
    offset2xx = sa.Column('offset2xx', sa.Numeric(8, 3), default=None)
    offset6xx = sa.Column('offset6xx', sa.Numeric(8, 3), default=None)
    dt_modify = sa.Column('dt_modify', sa.DateTime,
                          default=datetime.datetime.utcnow,
                          onupdate=datetime.datetime.utcnow)

    kiosk = relationship('Kiosk')

    sync_filter_rules = [
        lambda request: (KioskCalibration.kiosk == request.kiosk),
    ]

    @validates('retry')
    @model_validator
    def check_retry(self, key, value):
        try:
            validate_float_gt_or_eq_zero(value)
            validate_numeric(value, 5, 3)
            return float(value)
        except ValueError:
            if not value:
                raise ValidationError("Retry value can't be empty")
            else:
                raise ValidationError("Retry value is not numeric. Give number, please")
        except Exception, e:
            raise ValidationError(e.message)

    @validates('top_offset', 'bottom_offset', 'exchange_offset', 'pulses_per_slot', 'distance1', 'distance2', 'offset2xx', 'offset6xx')
    @model_validator
    def check_numeric(self, key, value):
        try:
            validate_numeric(value, 5, 3)
            return value
        except ValueError:
            if not value:
                raise ValidationError("Retry value can't be empty")
            else:
                raise ValidationError("Retry value is not numeric. Give number, please")
        except Exception, e:
            raise ValidationError(e.message)

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        ExtMixin.__init__(self)

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @property
    def robot_retry(self):
        return self.retry

    @robot_retry.setter
    def robot_retry(self, value):
        self.retry = value