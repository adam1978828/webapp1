# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Kalpakchi'


class UpdateMoviesStatsAlt(Base):
    __tablename__ = u's_update_movies_stats_alt'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    _detected = sa.Column('detected', sa.Numeric(10, 0), default=0)
    _existed = sa.Column('existed', sa.Numeric(10, 0), default=0)
    _not_recognized = sa.Column('not_recognized', sa.Numeric(10, 0), default=0)
    _stored = sa.Column('stored', sa.Numeric(10, 0), default=0)
    _hash_handled = sa.Column('hash_handled', sa.Numeric(10, 0), default=0)
    total = sa.Column('total', sa.Numeric(10, 0), default=0)
    _status_id = sa.Column('status_id', sa.Numeric(2, 0), sa.ForeignKey('movie_data_load_status.id'), default=None)
    update_type_id = sa.Column('update_type_id', sa.Numeric(1, 0), sa.ForeignKey('movie_data_load_type.id'), default=None)
    message = sa.Column('message', sa.String(512), default='')
    dt_start = sa.Column('dt_start', sa.DateTime,
                         default=datetime.datetime.utcnow)
    dt_end = sa.Column('dt_end', sa.DateTime)
    dt_modify = sa.Column('dt_modify', sa.DateTime,
                          default=datetime.datetime.utcnow,
                          onupdate=datetime.datetime.utcnow)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'))

    user = relationship('User')
    _status = relationship('MovieDataLoadStatus')
    update_type = relationship('MovieDataLoadType')

    @property
    def detected(self):
        return self._detected

    @detected.setter
    def detected(self, value):
        self._detected = value
        self.save()

    @property
    def existed(self):
        return self._existed

    @existed.setter
    def existed(self, value):
        self._existed = value
        self.save()

    @property
    def hash_handled(self):
        return self._hash_handled

    @hash_handled.setter
    def hash_handled(self, value):
        self._hash_handled = value
        self.save()

    @property
    def not_recognized(self):
        return self._not_recognized

    @not_recognized.setter
    def not_recognized(self, value):
        self._not_recognized = value
        self.save()

    @property
    def stored(self):
        return self._stored

    @stored.setter
    def stored(self, value):
        self._stored = value
        self.save()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status_id = value
        self.save()

    def save(self):
        object_session(self).commit()