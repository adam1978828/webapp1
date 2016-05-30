# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session
from base import Base
from movie_genre_translation import MovieGenreTranslation

__author__ = 'D.Ivanets, D.Kalpakchi'


class MovieGenre(Base):
    __tablename__ = u'e_movie_genre'
    __table_args__ = {'sqlite_autoincrement': True}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True, )

    translation = relationship("MovieGenreTranslation")

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    def get_translation(self, language):
        # return object_session(self).query(MovieGenreTranslation).with_parent(self).\
        #     filter(MovieGenreTranslation.language == language).first()
        return object_session(self).query(MovieGenreTranslation).filter_by(movie_genre_id=self.id)\
            .filter_by(language_id=language.id).first()

    @property
    def get_title(self):
        return object_session(self).query(MovieGenreTranslation.value).filter_by(movie_genre_id=self.id)\
            .filter_by(language_id=1).scalar()
