# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from base import Base, ExtMixin
from libs.validators.core import model_validator, validate_length_of, validate_numericality_of
from libs.validators.string_validators import validate_is_not_numeric, validate_string_not_empty


__author__ = 'D.Ivanets, D.Kalpakchi'


class Address(Base, ExtMixin):
    __tablename__ = u'c_address'
    __table_args__ = {}
    id = sa.Column('id', sa.NUMERIC(10, 0), primary_key=True)
    line_1 = sa.Column('line_1', sa.String(120), default='')
    line_2 = sa.Column('line_2', sa.String(120), default='')
    #line_3 = sa.Column('line_3', sa.String(120), default='')
    city = sa.Column('city', sa.String(100), default='')
    state = sa.Column('state', sa.String(50), default='')
    postalcode = sa.Column('postalcode', sa.String(16), default='')
    country = sa.Column('country', sa.String(50), default='')
    latitude = sa.Column('latitude', sa.Float(15))
    longitude = sa.Column('longitude', sa.Float(15))

    @validates('line_1', 'line_2')
    @model_validator
    def check_line_1(self, key, value):
        validate_length_of(value, min_value=0, max_value=120)
        if len(value):
            validate_is_not_numeric(value)
        return value

    @validates('city')
    @model_validator
    def check_city(self, key, value):
        validate_length_of(value, min_value=0, max_value=100)
        if len(value):
            validate_is_not_numeric(value)
        return value

    @validates('state', 'country')
    @model_validator
    def check_state_or_country(self, key, value):
        validate_length_of(value, min_value=0, max_value=50)
        if len(value):
            validate_is_not_numeric(value)
        return value

    @validates('postalcode')
    @model_validator
    def check_postalcode(self, key, value):
        validate_length_of(value, min_value=0, max_value=16)
        if len(value):
            validate_numericality_of(value)
        return value

    @validates('latitude', 'longitude')
    @model_validator
    def check_geolocation(self, key, value):
        if value:
            validate_string_not_empty(value if type(value) == str else str(value))
        else:
            return None
        return value

    def __init__(self):
        ExtMixin.__init__(self)

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    def to_string(self):
        # return ", ".join([item for item in [self.line_1, self.line_2, self.city, self.state, self.postalcode] if item]) \
        #            .replace(', , ', ', ') or ''
        return self.line_1

    @hybrid_property
    def lat_long(self):
        return (self.latitude, self.longitude)