# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy import or_

from .base import Base


__author__ = 'D.Ivanets'


class VideoFile(Base):
    __tablename__ = 'v_video_file'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'), nullable=True)
    name = sa.Column('name', sa.String(40), default='')
    alias = sa.Column('alias', sa.String(128), default='')
    length = sa.Column('length', sa.Numeric(5, 0), default=0)
    hash = sa.Column('hash', sa.String(32), default='')
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    company = relationship('Company', uselist=False)

    sync_filter_rules = [lambda request: or_(VideoFile.company == request.kiosk.company, VideoFile.company_id == None), ]

    def __init__(self, company_id=None, name=None, alias=None):
        if company_id:
            self.company_id = company_id
        if name:
            self.name = name
        if alias:
            self.alias = alias

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()
