# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Ivanets'


class KioskBashCommand(Base):
    __tablename__ = u'k_kiosk_bash_command'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'))
    user_id = sa.Column('user_id', sa.String(36, 0), sa.ForeignKey('c_user.id'))
    command = sa.Column('command', sa.Text, default='')
    exec_result = sa.Column('exec_result', sa.Text, default=None)
    exec_err = sa.Column('exec_err', sa.Text, default=None)
    dt_create = sa.Column('dt_create', sa.DateTime, default=datetime.datetime.utcnow)
    dt_executed = sa.Column('dt_used', sa.DateTime)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    kiosk = relationship('Kiosk', uselist=False)
    user = relationship('User', uselist=False)

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()

    def send(self):
        self.dt_executed = datetime.datetime.utcnow()