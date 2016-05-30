# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base
from sqlalchemy.orm import relationship
import datetime

class Report(Base):
    __tablename__ = 'rep_report'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    name = sa.Column('name', sa.VARCHAR(1024), default='')
    pattern_id = sa.Column('pattern_id', sa.Numeric, sa.ForeignKey('rep_report_pattern.id'))
    report = sa.Column('report', sa.VARCHAR(200), default='')
    html_content = sa.Column('html_content', sa.Text, default='')
    xls_content = sa.Column('xls_content', sa.Text, default='')
    dt_create = sa.Column('dt_create', sa.DateTime, default=datetime.datetime.utcnow)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'))

    pattern = relationship('ReportPattern')
    user = relationship('User')
    company = relationship('Company')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()