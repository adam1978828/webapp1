# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates

from .base import Base, ExtMixin
from libs.validators.core import model_validator, validate_length_of
from libs.validators.string_validators import validate_string_hex

__author__ = 'D.Ivanets, D.Kalpakchi'


class Disk(Base, ExtMixin):
    __tablename__ = u'disk'
    __table_args__ = {}
    rf_id = sa.Column('rf_id', sa.String(18), primary_key=True)
    slot_id = sa.Column('slot_id', sa.Numeric(10, 0), sa.ForeignKey('k_slot.id'))
    upc_link = sa.Column('upc', sa.String(20), sa.ForeignKey('upc.upc'))
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'))
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'))
    state_id = sa.Column('state_id', sa.Numeric(2, 0))
    disk_condition_id = sa.Column('disk_condition_id', sa.Numeric(1, 0),
                                  sa.ForeignKey('e_disk_condition.id'), default=1)
    dt_modify = sa.Column('dt_modify', sa.DateTime,
                          default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    upc = relationship("UPC")
    kiosk = relationship("Kiosk", secondary='k_slot', uselist=False)
    company = relationship("Company")
    disk_condition = relationship('DiskCondition', backref='disk')
    disk_photo = relationship('DiskPhoto', uselist=False, order_by='desc(DiskPhoto.dt_modify)')
    slot = relationship('Slot', uselist=False)

    sync_filter_rules = [lambda request: (Disk.company == request.kiosk.company), ]

    @validates('rf_id')
    @model_validator
    def check_rf_id(self, key, value):
        validate_length_of(value, min_value=18, max_value=18)
        validate_string_hex(value)
        return value

    def __init__(self, rf_id=None, upc=None, kiosk=None, state=0):
        ExtMixin.__init__(self)
        if rf_id:
            self.rf_id = rf_id
        self.upc = upc
        if kiosk:
            self.kiosk = kiosk
        self.state_id = state

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    def set_state(self, state):
        self.state_id = state

    def __repr__(self):
        return u"<%s(%s/%s/%s)>" % (self.__class__.__name__, self.rf_id, self.upc_link, self.kiosk_id)

    def __unicode__(self):
        return self.__repr__()

    def calculate_rent(self):
        disk_kiosk = self.slot.kiosk
        # if kisok, if slot etc
        settings = disk_kiosk.settings
        # actual_tariff count with tp
        actual_tariff = disk_kiosk.tariff_value
        tax_rate = float(settings.rent_tax_rate) / 100.0
        first_night_tariff = float(actual_tariff.first_night)
        sub_total = first_night_tariff
        taxes = tax_rate * sub_total
        return (round(sub_total, 2), round(taxes, 2), round(sub_total + taxes, 2))
