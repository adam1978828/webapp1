# -*- coding: utf-8 -*-
import sqlalchemy as sa
from Model.base import Base
from sqlalchemy.orm import relationship


class RepDataSource(Base):
    __tablename__ = 'rep_data_source'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    name = sa.Column('name', sa.VARCHAR(100), default='', unique=True)
    alias = sa.Column('alias', sa.VARCHAR(100), default='', unique=True)
    source = sa.Column('source', sa.Text, default='')
    source_type = sa.Column('source_type', sa.VARCHAR(20), default='')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()


class RepDataSourceField(Base):
    __tablename__ = 'rep_data_source_field'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    column_name = sa.Column('column_name', sa.VARCHAR(200), default='')
    name = sa.Column('name', sa.VARCHAR(200), default='')
    column_width = sa.Column('column_width', sa.Numeric(10, 0), default=None)
    allow_ordering = sa.Column('allow_ordering', sa.Numeric(1, 0), default=None)
    allow_grouping = sa.Column('allow_grouping', sa.Numeric(1, 0), default=None)
    allow_display = sa.Column('allow_display', sa.Numeric(1, 0), default=None)
    field_type = sa.Column('field_type', sa.VARCHAR(20), default='')
    data_source_id = sa.Column('data_source_id', sa.Numeric, sa.ForeignKey('rep_data_source.id'))
    order_num = sa.Column('order_num', sa.Numeric(10, 0), default=None)
    need_sub_total = sa.Column('need_sub_total', sa.Numeric(1, 0), default=0)
    data_source = relationship('RepDataSource')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()


class RepDataSourceFieldAggregation(Base):
    __tablename__ = 'rep_data_source_field_aggregation'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    field_id = sa.Column('field_id', sa.Numeric, sa.ForeignKey('rep_data_source_field.id'))
    aggregation_type = sa.Column('aggregation_type', sa.VARCHAR(20), default='')

    field = relationship('RepDataSourceField')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()


class RepDataSourceFieldFilter(Base):
    __tablename__ = 'rep_data_source_field_filter'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    field_id = sa.Column('field_id', sa.Numeric, sa.ForeignKey('rep_data_source_field.id'))
    column_name = sa.Column('column_name', sa.VARCHAR(200), default='')
    source = sa.Column('source', sa.Text, default='')
    source_key_column = sa.Column('source_key_column', sa.VARCHAR(200), default='')
    source_val_column = sa.Column('source_val_column', sa.VARCHAR(200), default='')
    source_type = sa.Column('source_type', sa.VARCHAR(20), default='')

    field = relationship('RepDataSourceField')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()


class RepDataSourceFieldFilterOperation(Base):
    __tablename__ = 'rep_data_source_field_filter_operation'
    __table_args__ = {}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    filter_id = sa.Column('filter_id', sa.Numeric, sa.ForeignKey('rep_data_source_field_filter.id'))
    operation = sa.Column('operation', sa.VARCHAR(100), default='')

    filter = relationship('RepDataSourceFieldFilter')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.id,)

    def __unicode__(self):
        return self.__repr__()