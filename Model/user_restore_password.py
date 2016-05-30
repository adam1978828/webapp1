# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy import inspect
from base import Base, ExtMixin
from WebApp.utils import random_string

__author__ = 'D.Ivanets, D.Kalpakchi'


class UserRestorePassword(Base, ExtMixin):
    __tablename__ = u'c_user_restore_password'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10), primary_key=True)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))
    change_pass_code = sa.Column('change_pass_code', sa.String(32))
    dt_create = sa.Column(
        'dt_create', sa.DateTime, default=datetime.datetime.utcnow)
    dt_use = sa.Column('dt_use', sa.DateTime)

    user = relationship('User')
    company = relationship('Company', secondary='c_user', uselist=False)

    def __init__(self, user):
        ExtMixin.__init__(self)
        self.user = user
        self.change_pass_code = random_string(32)

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    def done(self, new_password, field_name='password'):
        self.user.set_password(new_password, field_name)
        if self.user.no_errors():
            self.dt_use = datetime.datetime.utcnow()
            inspect(self).session.commit()
        else:
            self.errors.extend(self.user.errors)

    def __repr__(self):
        return u"<%s(%s:%s:%s)>" % (self.__class__.__name__, self.id, self.user.email, self.change_pass_code)

    def __unicode__(self):
        return self.__repr__()
