# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base
from libs.utils.url_functions import construct_url

__author__ = 'D.Kalpakchi'


class CompanySocialCommunity(Base):
    __tablename__ = 'c_social_community'
    __table_args__ = {}
    id = sa.Column('id', sa.Integer, primary_key=True)
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'))
    brand_id = sa.Column('brand_id', sa.Integer, sa.ForeignKey('e_social_communities_brands.id'))
    alias = sa.Column('alias', sa.String(50))
    logo_path = sa.Column('logo_path', sa.String(255))
    url = sa.Column('url', sa.String(255), nullable=False)

    company = relationship('Company', uselist=False)
    brand = relationship('SocialCommunityBrand')

    def __init__(self, company_id, brand_id, url):
        self.company_id = company_id
        self.brand_id = brand_id
        self.url = construct_url(url)

    def __repr__(self):
        return u"<%s(%s/%s)>" % (self.__class__.__name__, self.brand, self.url)

    def __unicode__(self):
        return self.__repr__()
