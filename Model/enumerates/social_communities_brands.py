# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from ..base import Base
from libs.utils.url_functions import construct_url

__author__ = 'D.Kalpakchi'


class SocialCommunityBrand(Base):
    __tablename__ = 'e_social_communities_brands'
    __table_args__ = {}
    id = sa.Column('id', sa.Integer, primary_key=True)
    brand = sa.Column('brand', sa.String(20), nullable=False)
    alias = sa.Column('alias', sa.String(50))

    def __init__(self, brand, alias = None):
        self.brand = brand
        self.alias = alias

    def __repr__(self):
        return u"<%s(%s/%s)>" % (self.__class__.__name__, self.brand, self.alias)

    def __unicode__(self):
        return self.__repr__()
