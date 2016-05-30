# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class MovieGenreTranslation(Base):
    __tablename__ = u'e_movie_genre_translation'
    __table_args__ = {'sqlite_autoincrement': True}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True, )
    movie_genre_id = sa.Column(
        'movie_genre_id', sa.Numeric, sa.ForeignKey("e_movie_genre.id"))
    language_id = sa.Column(
        'language_id', sa.Numeric, sa.ForeignKey("e_language.id"))
    value = sa.Column('value', sa.String(64))

    movie_genre = relationship("MovieGenre")
    language = relationship("Language")

    def __init__(self, movie_genre=None, language=None, value=''):
        if movie_genre:
            self.movie_genre = movie_genre
        if language:
            self.language = language
        self.value = value

    def __repr__(self):
        return u"<%s(%s:%s:'%s')>" % (self.__class__.__name__, self.id, self.language.short_name, self.value)
        # return u"<%s>\n" \
        #        u"\tID:    %s\n" \
        #        u"\tLang:  %s\n" \
        #        u"\tValue: %s" % (self.__class__.__name__, self.id, self.language.short_name, self.value)

    def __unicode__(self):
        return self.__repr__()
