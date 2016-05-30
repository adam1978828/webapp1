# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base


__author__ = 'D.Ivanets, D.Kalpakchi'


class DisksView(Base):
    __tablename__ = u'disks_view'
    __table_args__ = {}
    company_id = sa.Column('company_id', sa.Numeric(10))
    company_name = sa.Column('company_name', sa.String(255))

    kiosk_alias = sa.Column('kiosk_alias', sa.String(128))
    kiosk_rented_alias = sa.Column('kiosk_rented_alias', sa.String(128))

    disk_rfid = sa.Column('disk_rfid', sa.String(18), primary_key=True)
    disk_upc = sa.Column('disk_upc', sa.String(20))
    disk_format = sa.Column('disk_format', sa.String(10))
    disk_state = sa.Column('disk_state', sa.String(10))

    movie_name = sa.Column('movie_name', sa.String(128))
    movie_release_date = sa.Column('movie_release_date', sa.String(120))
    movie_dvd_release_date = sa.Column('movie_dvd_release_date', sa.String(120))
    deal_start_date = sa.Column('deal_start_date', sa.String(120))

    kiosk_slot_number = sa.Column('kiosk_slot_number', sa.Numeric(3, 0))

    rent_days = sa.Column('rent_days', sa.Numeric(10))
    deal_first_night_rent_charge = sa.Column('deal_first_night_rent_charge', sa.Numeric(10))
    deal_next_night_rent_charge = sa.Column('deal_next_night_rent_charge', sa.Numeric(10))
    deal_sale_charge = sa.Column('deal_sale_charge', sa.Numeric(10))
    deal_total_amount = sa.Column('deal_total_amount', sa.Numeric(10))
    is_in_rent = sa.Column('is_in_rent', sa.Numeric(1))

    def __repr__(self):
        return u"<%s(%s)>" % (self.__class__.__name__, self.disk_rf_id,)

    def __unicode__(self):
        return self.__repr__()