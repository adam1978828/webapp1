# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from base import Base


__author__ = 'D.Ivanets, D.Kalpakchi'


class MoviesView(Base):
    __tablename__ = u'movies_view'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    upc = sa.Column('upc', sa.String(128))
    title = sa.Column('title', sa.String(128))
    length = sa.Column('length', sa.Numeric(4, 0))
    dt_release = sa.Column('dt_release', sa.Date())
    dt_dvd_release = sa.Column('dt_dvd_release', sa.Date())
    rating = sa.Column('rating', sa.String(10))
    dt_modify = sa.Column('dt_modify', sa.Date())

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.movie__id,)

    def __unicode__(self):
        return self.__repr__()