# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base

__author__ = 'D.Ivanets'


class Language(Base):
    __tablename__ = u'e_language'
    __table_args__ = {'sqlite_autoincrement': True}
    id = sa.Column('id', sa.Numeric, primary_key=True)
    short_name = sa.Column('short_name', sa.String(4))
    name = sa.Column('name', sa.String(50))

    def __init__(self, name='', short_name=''):
        self.name = name
        self.short_name = short_name

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.id, self.short_name)
