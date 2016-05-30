# -*- coding: utf-8 -*-
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base

__author__ = 'D.Kalpakchi'


class ReservationCart(Base):
    __tablename__ = u'd_reservation_cart'
    __table_args__ = {}
    upc_link = sa.Column('upc', sa.String(20), sa.ForeignKey('upc.upc'), primary_key=True)
    kiosk_id = sa.Column('kiosk_id', sa.Numeric(10, 0), sa.ForeignKey('c_kiosk.id'), primary_key=True)
    user_id = sa.Column('user_id', sa.String(36), sa.ForeignKey('c_user.id'), primary_key=True)
    disk_format_id = sa.Column('disk_format_id', sa.Numeric(1, 0), sa.ForeignKey('e_disk_format.id'))
    coupon_id = sa.Column('coupon_id', sa.Numeric, sa.ForeignKey('d_coupon.id'))
    discount = sa.Column('discount', sa.Numeric(7, 2), default=0)
    is_reserved = sa.Column('is_reserved', sa.Boolean, default=False)
    is_available = sa.Column('is_available', sa.Boolean, default=False, nullable=False)
    dt_added = sa.Column('dt_added', sa.DateTime, default=datetime.datetime.utcnow)

    upc = relationship('UPC')
    kiosk = relationship('Kiosk')
    user = relationship('User')
    coupon = relationship('Coupon')
    disk_format = relationship('DiskFormat')

    def __init__(self, upc=None, kiosk_id=None, format_id=None, user_id=None):
        if upc:
            self.upc_link = upc
        if kiosk_id:
            self.kiosk_id = kiosk_id
        if format_id:
            self.disk_format_id = format_id
        if user_id:
            self.user_id = user_id
        self.is_available = True

    def __repr__(self):
        return "<%s(%s/%s/%s)>" % (
            self.__class__.__name__, self.upc, self.kiosk_id, self.user_id)

    def __unicode__(self):
        return self.__repr__()        
