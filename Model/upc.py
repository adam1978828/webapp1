# -*- coding: utf-8 -*-
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session, validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.elements import or_

from base import Base, ExtMixin
from company_upc_tariff_plan import CompanyUpcTariffPlan
from libs.validators.core import model_validator, validate_numericality_of, validate_length_of
from libs.validators.string_validators import validate_string_not_empty


__author__ = 'D.Ivanets, D.Kalpakchi'


class UPC(Base, ExtMixin):
    __tablename__ = u'upc'
    __table_args__ = {}
    upc = sa.Column('upc', sa.String(20), primary_key=True)
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    hti_id = sa.Column('hti_id', sa.Numeric(10, 0))

    upc_movie = relationship('UpcMovie', uselist=False)
    format = relationship('DiskFormat', secondary='d_upc_movie', uselist=False)
    movie = relationship('Movie', secondary='d_upc_movie', uselist=False)
    sound = relationship('Language', secondary='d_upc_sound')
    subtitle = relationship('Language', secondary='d_movie_subtitle')
    disk = relationship("Disk")
    reservation_cart = relationship("ReservationCart")

    def set_content(self, content):
        from Model import Movie

        if isinstance(content, Movie):
            self.movie = content

    def __init__(self, upc=None, movie=None, sound=None, subtitles=None):
        ExtMixin.__init__(self)
        if upc:
            self.upc = upc
        if movie:
            self.movie = movie
        self.sound = sound or []
        self.subtitle = subtitles or []

    @sa.orm.reconstructor
    def init_on_load(self):
        ExtMixin.__init__(self)

    @model_validator
    @validates('upc')
    def check_upc(self, key, value):
        validate_string_not_empty(value)
        validate_numericality_of(value)
        validate_length_of(value, min_value=12, max_value=20)
        return value

    def __repr__(self):
        # return u"<%s(%s)>" % (self.__class__.__name__, self.upc,)
        return (u"<%s>\n"
                u"UPC:   %s\n"
                u"Movie: %s\n"
                u"DT_md: %s"
                % (self.__class__.__name__, self.upc, self.movie, self.dt_modify)).replace('\n', '\n\t')

    def __unicode__(self):
        return self.__repr__()

    @property
    def tariff_plan_name(self):
        tariff = self.tariff_plan
        return tariff.name if tariff else "No price plan yet"

    @hybrid_property
    def tariff_plan(self):
        return object_session(self).query(CompanyUpcTariffPlan).filter_by(upc_link=self.upc).first()

    def get_tariff_value(self, kiosk):
        from Model import TariffValue
        t_plan = kiosk.company.upc_tariff_plans.filter_by(upc=self).first()
        if not t_plan:
            if self.format.id == 1:
                t_plan = kiosk.settings.dvd_tariff_plan or \
                    kiosk.company.company_settings.dvd_tariff_plan
            elif self.format.id == 2:
                t_plan = kiosk.settings.blu_ray_tariff_plan or \
                    kiosk.company.company_settings.blu_ray_tariff_plan
            else:
                msg = 'Incorrect UPC.format.id: {}'.format(self.format.id)
                raise RuntimeError(msg)
        else:
            t_plan = t_plan.tariff_plan
        t_value = t_plan.tariff_value\
            .filter(or_(TariffValue.kiosk_id == kiosk.id,
                        None == TariffValue.kiosk_id)) \
            .order_by(TariffValue.dt_end.desc(), TariffValue.kiosk_id) \
            .first()
        return t_value