# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


__author__ = 'D.Ivanets'


class CompanyKioskManager(Base):
    __tablename__ = 'c_company_kiosk_manager'
    __table_args__ = {}
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'), primary_key=True)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'), primary_key=True)

    company = relationship('Company')
    user = relationship('User')

    def __init__(self, company_id, user_id):
        self.company_id = company_id
        self.user_id = user_id

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.company_id, self.user_id)

    def __unicode__(self):
        return self.__repr__()
