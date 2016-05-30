# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates
from base import Base, ExtMixin

from libs.validators.core import model_validator
from libs.validators.string_validators import validate_string_not_empty


__author__ = 'D.Ivanets, D.Kalpakchi'


class MovieTranslation(Base, ExtMixin):
    __tablename__ = u'd_movie_translation'
    __table_args__ = {'sqlite_autoincrement': True}

    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True, )
    movie_id = sa.Column('movie_id', sa.Numeric, sa.ForeignKey("d_movie.id"))
    language_id = sa.Column('language_id', sa.Numeric, sa.ForeignKey("e_language.id"))
    name = sa.Column('name', sa.String(128))
    description = sa.Column('description', sa.String(2048))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    movie = relationship("Movie")
    language = relationship("Language")

    def __init__(self, name='', description='', lang=None, movie=None):
        ExtMixin.__init__(self)
        self.movie = movie
        self.name = name
        self.description = description
        if lang:
            self.language = lang
        else:
            self.language_id = 1

    @sa.orm.reconstructor
    def init_on_load(self): 
        ExtMixin.__init__(self)

    @model_validator
    @validates('title')
    def check_title(self, key, value):
        validate_string_not_empty(value)
        return value

    def __repr__(self):
        # return u"<%s(%s:%s:'%s')>" % (self.__class__.__name__, self.id,
        # self.language.short_name, self.name)
        return (u"<%s>\n"
                u"Name:  %s\n"
                u"Descr: %s "
                % (self.__class__.__name__, self.name,
                   self.description[:50].replace('\n', ''))).replace('\n', '\n\t')

    def __unicode__(self):
        return self.__repr__()