# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates
from base import Base, ExtMixin

from libs.validators.core import model_validator
from libs.validators.string_validators import validate_string_not_empty

__author__ = 'D.Ivanets'


class UpcMovie(Base, ExtMixin):
    __tablename__ = u'd_upc_movie'
    __table_args__ = {}
    movie_id = sa.Column('movie_id', sa.Numeric, sa.ForeignKey('d_movie.id'))
    upc = sa.Column(
        'upc', sa.String(20), sa.ForeignKey('upc.upc'), primary_key=True)
    disk_format_id = sa.Column(
        'disk_format_id', sa.Numeric, sa.ForeignKey('e_disk_format.id'))
    dt_modify = sa.Column(
        'dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    disk_format = relationship('DiskFormat')
    movie = relationship('Movie')
    # upc = relationship('UPC')

    def __init__(self, upc, movie_id, format_id):
        ExtMixin.__init__(self)
        self.upc = upc
        self.movie_id = movie_id
        self.disk_format_id = format_id

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    @validates('disk_format_id')
    @model_validator
    def check_ids(self, key, value):
        validate_string_not_empty(value)
        return int(value)

    @validates('upc')
    @model_validator
    def check_upc(self, key, value):
        validate_string_not_empty(value)
        return value

    def __repr__(self):
        return u"<%s(%s/%s/%s)>" % (self.__class__.__name__, self.upc, self.movie_id, self.disk_format_id)

    def __unicode__(self):
        return self.__repr__()
