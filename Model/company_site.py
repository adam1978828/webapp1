# -*- coding: utf-8 -*-
import datetime
from django.core.exceptions import ValidationError

from django.core.validators import validate_email
import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates
from sqlalchemy.orm.session import object_session

from base import Base, ExtMixin
from libs.validators.core import model_validator
from libs.validators.string_validators import validate_url

__author__ = 'D.Kalpakchi, D.Ivanets'


class CompanySite(Base, ExtMixin):
    __tablename__ = 's_company_site'
    __table_args__ = {}
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'), primary_key=True)
    domain = sa.Column('domain', sa.String(100), default=None, nullable=True, unique=True)
    name = sa.Column('name', sa.String(100), default='', nullable=False)
    logo_path = sa.Column('logo_path', sa.String(128))
    support_email = sa.Column('support_email', sa.String(128), nullable=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow)

    company = relationship('Company', uselist=False)

    def __init__(self, company_id=None):
        ExtMixin.__init__(self)
        self.company_id = company_id

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.domain,)

    def __unicode__(self):
        return self.__repr__()

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    @validates('support_email')
    @model_validator
    def check_support_email(self, key, value):
        if not value:
            return None
        validate_email(value)
        return value

    @validates('domain')
    @model_validator
    def check_domain(self, key, value):
        if not value:
            return None
        not_first_save = object_session(self).query(CompanySite)\
            .filter_by(company_id = self.company_id)\
            .first()
        if not_first_save:
            dublicates = object_session(self).query(CompanySite)\
                .filter(CompanySite.domain == value, CompanySite.company_id != self.company_id)\
                .all()
            if dublicates:
                raise ValidationError('This domain name is already in use')
        validate_url(value)
        return value
