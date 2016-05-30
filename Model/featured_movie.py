# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class FeaturedMovie(Base):
    __tablename__ = 'c_featured_movie'
    __table_args__ = {}
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'), primary_key=True)
    movie_id = sa.Column('movie_id', sa.Numeric(10, 0), sa.ForeignKey('d_movie.id'), primary_key=True)
    is_active = sa.Column('is_active', sa.Boolean, default=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    company = relationship('Company')
    movie = relationship('Movie')

    load_filter_rules = [lambda request: (FeaturedMovie.is_active == True), ]
    sync_filter_rules = [lambda request: (FeaturedMovie.company == request.kiosk.company), ]

    def __init__(self, company_id=None, movie_id=None):
        if company_id:
            self.company_id = company_id
        if movie_id:
            self.movie_id = movie_id
        self.is_active = True
        self.dt_modify = datetime.datetime.utcnow()

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.company_id, self.movie_id)

    def __unicode__(self):
        return self.__repr__()
