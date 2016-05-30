# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class MovieMovieGenre(Base):
    __tablename__ = u'd_movie_movie_genre'
    __table_args__ = {}
    movie_id = sa.Column('movie_id', sa.Numeric, sa.ForeignKey('d_movie.id'), primary_key=True)
    movie_genre_id = sa.Column('movie_genre_id', sa.Numeric, sa.ForeignKey('e_movie_genre.id'), primary_key=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    movie = relationship('Movie')
    movie_genre = relationship('MovieGenre')

    def __init__(self, movie_id, genre_id):
        self.movie_id = movie_id
        self.movie_genre_id = genre_id

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.movie_id, self.movie_genre_id)

    def __unicode__(self):
        return self.__repr__()
