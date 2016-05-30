# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
import datetime
from .rep_report import Report


class ReportPattern(Base):
    __tablename__ = 'rep_report_pattern'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    name = sa.Column('name', sa.VARCHAR(1024), default='')
    alias = sa.Column('alias', sa.VARCHAR(64), default='')
    pattern = sa.Column('pattern', sa.VARCHAR(200), default='')
    dt_create = sa.Column('dt_create', sa.DateTime, default=datetime.datetime.utcnow)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'))
    is_for_company = sa.Column('is_for_company', sa.Numeric(1, 0), default=0)

    user = relationship('User')
    company = relationship('Company')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    def reports_count(self):
        return object_session(self).query(Report)\
                .filter(Report.pattern_id == self.id)\
                .count()