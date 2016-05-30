# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session, validates
from sqlalchemy.ext.hybrid import hybrid_property
from django.core.validators import validate_email, URLValidator

from .base import Base, ExtMixin
from .card import Card
from .company_settings import CompanySettings
from libs.validators.core import validate_length_of, model_validator, validate_card_expiry
from django.core.exceptions import ValidationError


__author__ = 'D.Ivanets'


class Company(Base, ExtMixin):
    __tablename__ = u'c_company'
    __table_args__ = {'sqlite_autoincrement': True}
    id = sa.Column('id', sa.Numeric(10), primary_key=True)
    name = sa.Column('name', sa.String(255), default='')
    addr_id = sa.Column('addr_id', sa.Numeric(10), sa.ForeignKey('c_address.id'))
    phone = sa.Column('phone', sa.String(20), default='')
    alt_phone = sa.Column('alt_phone', sa.String(20), default='')
    email = sa.Column('email', sa.String(50), default='')
    web_site = sa.Column('web_site', sa.String(255), default='')
    card = sa.Column('card', sa.String(16), default='')
    cc_expiry = sa.Column('cc_expiry', sa.String(4))
    logo_path = sa.Column('logo_path', sa.String(255), default='')
    dt_modify = sa.Column('dt_modify', sa.DateTime,
                          default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    address = relationship('Address', backref='company')
    kiosks = relationship('Kiosk')
    user_groups = relationship('Group')
    users = relationship('User')
    tariff_plans = relationship('TariffPlan')
    payment_systems = relationship('CompanyPaymentSystem')
    company_settings = relationship('CompanySettings', uselist=False)
    featured_movies = relationship('Movie', secondary='c_featured_movie', lazy='dynamic')
    site = relationship('CompanySite', uselist=False)
    social_communities = relationship('CompanySocialCommunity')
    upc_tariff_plans = relationship('CompanyUpcTariffPlan', lazy='dynamic')
    alt_kiosks = relationship('Kiosk', lazy='dynamic')
    trailers = relationship('VideoFile', lazy='dynamic')

    sync_filter_rules = [lambda request: (Company.id == request.kiosk.company_id), ]

    @validates('email')
    @model_validator
    def check_email(self, key, value):
        if value:
            validate_email(value)
        return value

    @validates('web_site')
    @model_validator
    def check_url(self, key, value):
        if value:
            urlvalid = URLValidator()
            urlvalid(value)
        return value

    @validates('name')
    @model_validator
    def check_name(self, key, value):
        validate_length_of(value, min_value=3)
        return value

    @validates('cc_expiry')
    @model_validator
    def check_cc_expiry(self, key, value):
        if value:
            validate_card_expiry(value)
        return value

    @property
    def staff(self):
        return [user for user in self.users if user.user_type != 1]

    def __init__(self, name=''):
        ExtMixin.__init__(self)
        self.name = name
        #self.company_settings = CompanySettings()

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s:'%s')>" % (self.__class__.__name__, self.id, self.name)

    def __unicode__(self):
        return self.__repr__()

    # @hybrid_property
    def get_card_by_hash(self, card_hash):
        card = object_session(self).query(Card) \
            .filter_by(company=self) \
            .filter_by(hash=card_hash) \
            .first()
        return card

    @hybrid_property
    def geolocation(self):
        return self.address.lat_long

    @hybrid_property
    def has_geolocation(self):
        return bool(self.address.latitude and self.address.longitude)

    @hybrid_property
    def active_kiosks(self):
        return self.alt_kiosks.filter_by(is_running=True)