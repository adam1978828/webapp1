# -*- coding: utf-8 -*-
import uuid
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session, MapperExtension
from sqlalchemy.ext.hybrid import hybrid_property
from .slot import Slot
from base import Base, ExtMixin
from kiosk_settings import KioskSettings
from tariff_value import TariffValue
from kiosk_review import KioskReview
from WebApp.utils import alchemy_to_json, alchemy_from_json
from sqlalchemy import or_

__author__ = 'D.Ivanets, D.Kalpakchi'

dt_last_update = None


def on_update(context):
    if not sorted(['dt_modify', 'c_kiosk_id', 'dt_sync']) == sorted(context.compiled_parameters[0].keys()):
        return datetime.datetime.utcnow()
    else:
        return dt_last_update


class KioskExtension(MapperExtension):
    def before_update(self, mapper, connection, instance):
        """ Make sure when we update this record the created fields stay unchanged!  """
        # if not sorted(['dt_modify', 'c_kiosk_id', 'dt_sync']) == sorted(context.compiled_parameters[0].keys()):
        # instance.dt_modify = datetime.datetime.utcnow()
        global dt_last_update
        dt_last_update = instance.dt_modify


class Kiosk(Base, MapperExtension, ExtMixin):
    __tablename__ = u'c_kiosk'
    __table_args__ = {'sqlite_autoincrement': True}
    __mapper_args__ = {'extension': KioskExtension()}
    id = sa.Column('id', sa.Numeric(10, 0), primary_key=True)
    uuid = sa.Column('uuid', sa.String(32))
    company_id = sa.Column('company_id', sa.Numeric(10, 0), sa.ForeignKey('c_company.id'))
    addr_id = sa.Column('addr_id', sa.Numeric(10, 0), sa.ForeignKey('c_address.id'))
    dt_sync = sa.Column('dt_sync', sa.DateTime,
                        default=datetime.datetime.strptime("1900-01-01 00:00:00.000000", "%Y-%m-%d %H:%M:%S.%f"))
    dt_modify = sa.Column('dt_modify', sa.DateTime, default=datetime.datetime.utcnow, onupdate=on_update)
    activation_code = sa.Column('activation_code', sa.String(16), default='')
    is_running = sa.Column('is_running', sa.Boolean, default=True)
    is_not_deleted = sa.Column('is_not_deleted', sa.Boolean, default=True)
    group_number = sa.Column('group_number', sa.Numeric(10, 0), default=0)

    company = relationship('Company')
    disks = relationship("Disk", secondary='k_slot')
    address = relationship('Address', backref='kiosks')
    settings = relationship('KioskSettings', uselist=False)
    calibration = relationship('KioskCalibration', uselist=False)
    tariff_values = relationship('TariffValue')
    kiosk_screens = relationship('KioskScreens')
    slots = relationship('Slot', lazy='dynamic')
    video_schedule = relationship('VideoSchedule', lazy='dynamic')

    skip_days = relationship('KioskSkipWeekdays', secondary='c_kiosk_settings', lazy='dynamic')
    skip_dates = relationship('KioskSkipDates', secondary='c_kiosk_settings', lazy='dynamic')

    ordering_list = relationship('OrderingList', uselist=False)
    kiosk_actions = relationship('KioskAction', lazy='dynamic')
    kiosk_review = relationship('KioskReview', lazy='dynamic')

    def __init__(self, company=None, address=None):
        ExtMixin.__init__(self)
        self.uuid = uuid.uuid1().hex
        if address:
            self.address = address
        if company:
            self.company = company
            company_settings = alchemy_to_json(company.company_settings)
            if company_settings:
                kiosk_settings = {k: v for k, v in company_settings.iteritems() if k not in [u'company_id', u'id']}
            else:
                kiosk_settings = {}
            kiosk_settings[u'alias'] = 'New kiosk'
            self.settings = alchemy_from_json(KioskSettings, kiosk_settings)
        else:
            self.settings = KioskSettings(self)

    @sa.orm.reconstructor
    def init_on_load(self): 
        ExtMixin.__init__(self)

    def __repr__(self):
        return u"<%s(%s:%s)>" % (self.__class__.__name__, self.id, self.uuid)

    def __unicode__(self):
        return self.__repr__()

    @hybrid_property
    def actual_skip_days(self):
        return self.skip_days.filter_by(is_active=True)

    @hybrid_property
    def actual_skip_dates(self):
        return self.skip_dates.filter_by(is_active=True)

    def actual_tariff_value(self, tariff_plan):
        return object_session(self).query(TariffValue) \
            .filter_by(tariff_plan=tariff_plan) \
            .filter(or_(TariffValue.kiosk_id == self.id, None == TariffValue.kiosk_id)) \
            .order_by(TariffValue.dt_end.desc(), TariffValue.kiosk_id).first()

    def change_tariff(self, params=None):
        """
        Change current kiosk tariff value
        Ex.:
        kiosk.change_tariff({
            'tariff_plan': tariff_plan_values.first().tariff_plan,
            'first_night': first_night, 
            'next_night': next_night, 
            'sale': sale,
            'user': request.user
        })
        """
        if params:
            cur_tr_value = self.actual_tariff_value(params['tariff_plan'])

            tariff_value = TariffValue(params['tariff_plan'], self)
            tariff_value.first_night = params.get('first_night', '')
            tariff_value.next_night = params.get('next_night', '')
            tariff_value.sale = params.get('sale', '')
            tariff_value.sun_night = params.get('sun_night', '')
            tariff_value.mon_night = params.get('mon_night', '')
            tariff_value.tue_night = params.get('tue_night', '')
            tariff_value.wed_night = params.get('wed_night', '')
            tariff_value.thu_night = params.get('thu_night', '')
            tariff_value.fri_night = params.get('fri_night', '')
            tariff_value.sat_night = params.get('sat_night', '')
            tariff_value.user = params['user']
            tariff_value.kiosk = self
            current_time = datetime.datetime.utcnow()
            if tariff_value.no_errors():
                if cur_tr_value and cur_tr_value.kiosk_id:
                    cur_tr_value.dt_end = current_time
                tariff_value.dt_start = current_time
                object_session(self).add(tariff_value)
                # self.tariff_values.append(tariff_value)
            else:
                return tariff_value.errors

    @property
    def payment_system(self):
        p_s = self.settings.company_payment_system or self.company.company_settings.company_payment_system
        return p_s

    @property
    def status(self):
        status = {'status': 'DOWN', 'badge': 'red'}
        now = datetime.datetime.utcnow()
        if not self.dt_sync:
            status = {'status': 'NEVER UP', 'badge': 'blue light'}
        elif (now - self.dt_sync).seconds <= 90:
            status = {'status': 'OK', 'badge': 'green'}
        elif (now - self.dt_sync).seconds <= 180:
            status = {'status': 'PROBLEM', 'badge': 'orange'}
        return status

    @hybrid_property
    def geolocation(self):
        return self.address.lat_long

    @hybrid_property
    def has_geolocation(self):
        return bool(self.address.latitude and self.address.longitude)

    @hybrid_property
    def movies(self):
        return [disk.upc.movie for disk in self.disks if disk.slot.kiosk_id == self.id and
            disk.upc is not None and disk.slot.status_id == 1 and disk.state_id == 0]

    def get_free_slot(self, from_end=False, random=False):
        """
        :type from_end: bool
        :type random: bool
        :rtype: Slot
        """
        query = self.slots.filter_by(status_id=1).filter_by(disk=None)
        if from_end:
            query = query.order_by(Slot.number.desc())
        elif random:
            from sqlalchemy import func

            query = query.order_by(func.random())
        else:
            query = query.order_by(Slot.number)
        return query.first()

    def count_free_slots(self):
        """Counts number of empty slots
        :return: number of empty slots
        """
        query = self.slots\
            .filter_by(status_id=1)\
            .filter_by(disk=None)
        return query.count()

    def is_few_slots(self):
        """Checks if kiosk running low on empty slots
        :return: True, if there left less then minimal empty slots number
        :rtype: bool
        """
        if self.settings:
            return self.settings.empty_slots_warning >= self.count_free_slots()
        return False

    @property
    def tz_info(self):
        return self.settings.timezone.tz_info

    def retry_delta(self):
        minutes = int(self.settings.capture_retry_interval)
        return datetime.timedelta(minutes=minutes)

    @property
    def active_review_inventory(self):
        review_inventory = self.kiosk_review.filter(KioskReview.dt_end.is_(None)).first()
        return review_inventory


