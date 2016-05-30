# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base

__author__ = 'D.Ivanets'


class MovieRating(Base):
    __tablename__ = u'e_movie_rating'
    __table_args__ = {'sqlite_autoincrement': True}
    id = sa.Column('id', sa.Numeric, primary_key=True, )
    value = sa.Column('value', sa.String(10))

    def __init__(self, value=""):
        self.value = value

    def __repr__(self):
        return u"<%s(%s:'%s')>" % (self.__class__.__name__, self.id, self.value)
