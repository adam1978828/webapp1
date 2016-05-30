# -*- coding: utf-8 -*-
from dateutil import parser
import datetime
import uuid
from django.core.validators import validate_email
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.orm import relationship
from sys_function import SysFunction
from base import Base, ExtMixin
from libs.validators.core import validate_format_of, model_validator, validation_error, validate_length_of
from libs.validators.string_validators import validate_string_not_empty, validate_zip_code_string
from libs.utils.string_functions import convert2camelCase
from sqlalchemy.orm import validates

__author__ = 'D.Ivanets, D.Kalpakchi'


class User(Base, ExtMixin):
    __tablename__ = u'c_user'
    __table_args__ = {}
    id = sa.Column('id', sa.String(36), primary_key=True)
    first_name = sa.Column('first_name', sa.String(50), default='')
    last_name = sa.Column('last_name', sa.String(50), default='')
    email = sa.Column('email', sa.String(50), default='', unique=True)
    password = sa.Column('pass', sa.String(255), default='')
    salt = sa.Column('salt', sa.String(32), default='')
    company_id = sa.Column('company_id', sa.Numeric(10), sa.ForeignKey('c_company.id'))
    user_type_id = sa.Column('user_type_id', sa.Numeric(2), sa.ForeignKey('e_user_type.id'))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    phone = sa.Column('phone', sa.String(20), default='')
    m_phone = sa.Column('m_phone', sa.String(20), default='')
    email2 = sa.Column('email2', sa.String(50), default='')
    addr_id = sa.Column('addr_id', sa.Numeric(10), sa.ForeignKey('c_address.id'))

    preferred_kiosk_id = sa.Column('preferred_kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'))
    zip_code = sa.Column('zip_code', sa.String(5), default=None)

    is_su = sa.Column('is_su', sa.Boolean, default=False)
    is_email_valid = sa.Column('is_email_valid', sa.Boolean, default=False)
    local_tz = sa.Column('local_tz', sa.String(50))

    company = relationship('Company')
    user_type = relationship('UserType', backref='users')
    address = relationship('Address', backref='user')
    permissions = relationship('SysFunction', secondary='p_user_permission')
    groups = relationship('Group', secondary='p_user_to_group')
    cards = relationship('Card')

    preferred_kiosk = relationship("Kiosk")

    sync_filter_rules = [lambda request: (User.company == request.kiosk.company), ]

    @validates('first_name')
    @model_validator
    def check_first_name(self, key, value):
        validate_string_not_empty(value)
        return value

    @validates('last_name')
    @model_validator
    def check_last_name(self, key, value):
        validate_string_not_empty(value)
        return value

    @validates('zip_code')
    @model_validator
    def check_zip_code(self, key, value):
        validate_string_not_empty(value)
        validate_zip_code_string(value)
        return value

    @validates('email')
    @model_validator
    def check_email(self, key, value):
        validate_string_not_empty(value)
        validate_email(value)
        return value

    @validates('password')
    @model_validator
    def check_password(self, key, value):
        validate_string_not_empty(value)
        validate_format_of(value,
                           r'[A-Za-z0-9@#$%^&+=]{8,}', 'Password may contain upper or lower case letters, '
                                                       'numbers or symbols @#$%^&+=')
        return value

    def __init__(self, email=None, password=None, json_obj=None):
        ExtMixin.__init__(self)
        if json_obj:
            for key in json_obj:
                if key.startswith('dt_'):
                    self.__setattr__(key, parser.parse(json_obj[key]))
                else:
                    self.__setattr__(key, json_obj[key])
        else:
            self.id = str(uuid.uuid1())
            if email is not None:
                self.email = email
            if password is not None:
                self.set_password(password)

    @sa.orm.reconstructor
    def init_on_load(self): 
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s:'%s')>" % (self.__class__.__name__, self.id, self.email)

    def __unicode__(self):
        return self.__repr__()

    def rights_func(self):
        all_rights = []
        if self.is_su:
            if self.is_company:
                all_rights = inspect(self).session.query(
                    SysFunction).filter_by(for_company=True).all()
            if self.is_focus:
                all_rights = inspect(self).session.query(
                    SysFunction).filter_by(for_focus=True).all()
        else:
            all_rights = set(self.permissions)
            [all_rights.update(group.permissions) for group in self.groups]
        result = [perm.alias for perm in all_rights]
        return result

    @property
    def name(self):
        return (" ".join((self.first_name, self.last_name)).strip()) or self.email

    @property
    def full_name(self):
        return " ".join((self.first_name, self.last_name)).strip()

    @property
    def pk(self):
        return self.id

    @property
    def is_active(self):
        return True

    def is_pass_valid(self, password):
        import hashlib
        return self.password == hashlib.sha512(password + self.salt).hexdigest()

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    @property
    def is_focus(self):
        return self.user_type_id == 3

    @property
    def is_company(self):
        return self.user_type_id == 2

    def save(self, *args, **kwargs):
        session = inspect(self).session
        if session:
            inspect(self).session.commit()

    def set_password(self, password, field_name='password'):
        import uuid
        import hashlib

        try:
            validate_string_not_empty(password)
            validate_length_of(password, min_value=8)
            validate_format_of(password, r'(.)*[A-Za-z]+(.)*', 'Password must contain some letters')
            validate_format_of(password, r'(.)*[0-9]+(.)*', 'Password must contain some numbers')
            validate_format_of(password, r'(.)*[A-Z]+(.)*', 'Password must contain at least one UPPERCASE letter')
            self.salt = uuid.uuid4().hex
            self.password = hashlib.sha512(password + self.salt).hexdigest()
        except Exception, e:
            self.errors.append(validation_error(field_name, unicode(e.message)))

    def set_email_valid(self):
        self.is_email_valid = True

    @property
    def to_json(self):
        from encoder import AlchemyEncoder
        import json

        return json.loads(json.dumps(self, cls=AlchemyEncoder))


class AnonymousUser(object):
    id = None
    pk = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False

    def __init__(self):
        pass

    def __str__(self):
        return 'AnonymousUser'

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1  # instances always return the same hash value

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def set_password(self, raw_password):
        raise NotImplementedError

    def check_password(self, raw_password):
        raise NotImplementedError

    def get_group_permissions(self, obj=None):
        return set()

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

    def rights_func(self):
        return []

    def set_email_valid(self):
        raise NotImplementedError

    @property
    def is_focus(self):
        return False

    @property
    def is_company(self):
        return False