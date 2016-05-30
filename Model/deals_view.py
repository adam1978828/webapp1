# -*- coding: utf-8 -*-
import sqlalchemy as sa
from base import Base


__author__ = 'D.Ivanets, D.Kalpakchi'


class DealsView(Base):
    __tablename__ = u'deals_view'
    __table_args__ = {}
    deal_id = sa.Column('deal_id', sa.String(36), primary_key=True)
    deal_rf_id = sa.Column('deal_rf_id', sa.String(18))
    card_cardholder_name_n1_n2 = sa.Column('card_cardholder_name_n1_n2', sa.String(75))
    kiosk_settings_start_alias = sa.Column('kiosk_settings_start_alias', sa.String(128), default='')
    kiosk_settings_end_alias = sa.Column('kiosk_settings_end_alias', sa.String(128), default='')
    movie_translation_name = sa.Column('movie_translation_name', sa.String(128))
    movie_dt_release = sa.Column('movie_dt_release', sa.String(120))
    disk_format_name = sa.Column('disk_format_name', sa.String(10))
    company_id = sa.Column('company_id', sa.Numeric(10))
    company_name = sa.Column('company_name', sa.String(255))
    deal_status_alias = sa.Column('deal_status_alias', sa.String(16), default='')
    deal_dt_start = sa.Column('deal_dt_start', sa.String(120))
    deal_dt_end = sa.Column('deal_dt_end', sa.String(120))
    timezone_start_name = sa.Column('timezone_start_name', sa.String(32), default='')
    timezone_end_name = sa.Column('timezone_end_name', sa.String(32), default='')

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.deal__id,)

    def __unicode__(self):
        return self.__repr__()