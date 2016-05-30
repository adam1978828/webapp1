# -*- coding: utf-8 -*-
import datetime
import hashlib
import os

from django.conf import settings
import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates, object_session
from sqlalchemy.ext.hybrid import hybrid_property
from base import Base, ExtMixin
from movie_translation import MovieTranslation
from .enumerates.disk_format import DiskFormat
from upc_movie import UpcMovie
from upc import UPC
from disk import Disk
from slot import Slot
from sqlalchemy import and_

from libs.validators.core import model_validator, validate_numericality_of, validate_format_of
from libs.validators.core import validate_length_of

__author__ = 'D.Ivanets, D.Kalpakchi'


class Movie(Base, ExtMixin):
    __tablename__ = u'd_movie'
    __table_args__ = {'sqlite_autoincrement': True}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True, )
    length = sa.Column('length', sa.Numeric(4, 0))
    release_year = sa.Column('release_year', sa.Numeric(4, 0))
    dt_release = sa.Column('dt_release', sa.DateTime)
    movie_rating_id = sa.Column('movie_rating_id', sa.Numeric(2, 0), sa.ForeignKey("e_movie_rating.id"))
    img_path = sa.Column('img_path', sa.VARCHAR(128))
    bd_path = sa.Column('bd_path', sa.VARCHAR(128))
    tmdb_id = sa.Column('tmdb_id', sa.Numeric(10, 0))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_manual_edit = sa.Column('is_manual_edit', sa.Boolean, default=False)
    hash = sa.Column('hash', sa.VARCHAR(128))
    #omdb fields
    dt_dvd_release = sa.Column('dt_dvd_release', sa.DateTime)
    imdb_rating = sa.Column('imdb_rating', sa.Numeric(6, 2))
    imdb_id = sa.Column('imdb_id', sa.VARCHAR(128))
    box_office = sa.Column('box_office', sa.VARCHAR(128))

    upc = relationship('UPC', secondary='d_upc_movie')
    movie_genre = relationship('MovieGenre', secondary='d_movie_movie_genre')
    movie_rating = relationship("MovieRating")
    movie_translation = relationship('MovieTranslation', lazy='dynamic')
    featured = relationship('FeaturedMovie', lazy='dynamic')
    disk_formats = relationship('DiskFormat', secondary='d_upc_movie')

    def __init__(self, length=0, release_year=None, movie_rating=None,
                 img_path='', movie_translation=None,
                 movie_genre=None, dt_release=None, dt_dvd_release=None):
        ExtMixin.__init__(self)
        self.length = length
        if release_year:
            self.release_year = release_year
        if movie_rating:
            self.movie_rating = movie_rating
        self.img_path = img_path
        self.movie_translation = movie_translation or []
        self.movie_genre = movie_genre or []
        self.dt_release = dt_release
        self.dt_dvd_release = dt_dvd_release

    @sa.orm.reconstructor
    def init_on_load(self): 
        ExtMixin.__init__(self)

    @model_validator
    @validates('length')
    def check_length(self, key, value):
        if value:
            validate_length_of(value, min_value=0, max_value=4)
            validate_numericality_of(value)
            return int(value)
        else:
            return None

    @model_validator
    @validates('release_year')
    def check_release_year(self, key, value):
        validate_format_of(value, '[0-9]{4}')
        return int(value) if value else None

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    @property
    def get_name(self):
        m_t = self.movie_translation.filter_by(language_id=1).first()
        return m_t.name if m_t else "!!NONE!!"
        # en = [
        #     trans.name for trans in self.movie_translation if trans.language.short_name == 'en']
        # return en[0] if en else self.movie_translation[0].name if len(self.movie_translation) else "!!NONE!!"

    @property
    def get_description(self):
        m_t = self.movie_translation.filter_by(language_id=1).first()
        return m_t.description if m_t else "!!NONE!!"
        # en = [
        #     trans.description for trans in self.movie_translation if trans.language.short_name == 'en']
        # return en[0] if en else self.movie_translation[0].description if len(self.movie_translation) else "!!NONE!!"

    @property
    def languages(self):
        return [translation.language for translation in self.movie_translation]

    def language_string(self):
        return ", ".join([language.name for language in self.languages])

    @property
    def genre_string(self):
        return " | ".join([genre.get_title for genre in self.movie_genre])

    def disk_formats_in_kiosk(self, kiosk_id):
        return object_session(self).query(DiskFormat).join(UpcMovie).join(UPC).join(Disk).join(Slot)\
            .filter(and_(Slot.kiosk_id == kiosk_id, Disk.state_id == 0, UpcMovie.movie_id == self.id)).all()

    def available_disk_formats(self, company_id):
        return object_session(self).query(DiskFormat).join(UpcMovie).join(UPC).join(Disk)\
            .filter(and_(
                Disk.company_id == company_id,
                Disk.state_id == 0,
                UpcMovie.movie_id == self.id
            )).all()

    def upc_matching(self, format_id):
        try:
            return map(lambda x: x.upc, object_session(self).query(UpcMovie)\
                .filter_by(movie_id=self.id).filter_by(disk_format_id=format_id).all())
        except:
            return None

    def check_hash(self, full_path):
        if not os.path.isfile(full_path):
            return False
        movie_file = open(full_path)
        movie_hash = hashlib.md5(movie_file.read()).hexdigest()
        return movie_hash == self.hash