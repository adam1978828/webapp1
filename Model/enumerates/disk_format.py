# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ..base import Base

__author__ = 'D.Ivanets'


class DiskFormat(Base):
    __tablename__ = u'e_disk_format'
    __table_args__ = {'sqlite_autoincrement': True}

    id = sa.Column('id', sa.Numeric, primary_key=True, )
    name = sa.Column('name', sa.String(10))
    img_path = sa.Column('img_path', sa.String(64), default='')

    def __init__(self, name=''):
        self.name = name

    def __repr__(self):
        return u"<%s(%s:'%s')>" % (self.__class__.__name__, self.id, self.name)
