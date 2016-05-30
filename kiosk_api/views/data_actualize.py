# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import json
from datetime import datetime
import os
from pprint import pprint
from django.conf import settings

from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from Model import *
from WebApp.utils import z_alchemy_from_json, alchemy_list_to_json
import kiosk_api.utils
from upload_archive import log


__author__ = 'D.Ivanets'

data_sync_alias = 'db_data'
data_actions_alias = 'sort_actions'
actions_alias = 'actions'
data_bash_alias = 'bash_command'


@require_POST
@csrf_exempt
def data_actualize(request):
    """Used for synchronization data between kiosk and server
    """
    if not request.kiosk:
        return HttpResponseForbidden()

    files_in = None
    # print request.META.get(u'CONTENT_TYPE')
    if request.META.get(u'CONTENT_TYPE') == u'application/json':
        json_in = json.loads(request.body)
    else:
        files_in = request.FILES
        json_in = json.loads(request.POST[u'data'])
    pprint(json_in)
    data_actions_out = None

    if data_sync_alias in json_in:
        data_actions_in = json_in.get(data_actions_alias, '')
        # action_result = json_in.get(actions_alias, {})
        json_in = json_in.get(data_sync_alias, {})
    else:
        data_actions_in = None
        # action_result = {}

    current_time = datetime.utcnow()

    save_received_data(request, json_in, current_time, files_in)
    data_out = get_data_to_send(request, current_time)

    request.kiosk.dt_sync = current_time
    request.db_session.commit()

    if data_actions_in == 'OK' and request.kiosk.ordering_list:
        data_actions_out = ordering(request)
        if data_actions_out is None:
            request.db_session.delete(request.kiosk.ordering_list)
            request.db_session.commit()

    actions_out = {}
    for action in request.kiosk.kiosk_actions:
        if action.action_id == 2:
            actions_out[action.action.alias] = True
            request.db_session.delete(action)

    if data_actions_in is not None:
        data_out = {
            data_sync_alias: data_out,
            data_actions_alias: data_actions_out,
            data_bash_alias: get_next_bash_command(request),
            actions_alias: actions_out,
        }

    pprint(data_out)
    return JsonResponse(data_out)


def save_received_data(request, data_in, current_time, files):

    classes_to_save = [Card, Disk, Deal, Slot, KioskSettings,
                       KioskReview, KioskReviewSlot]

    request.db_session.autoflush = False
    for cls in classes_to_save:
        z_alchemy_from_json(alchemy_type=cls,
                            json_obj=data_in.get(cls.__tablename__, []),
                            session=request.db_session,
                            cur_time=current_time)

    for item in data_in.get(DiskPhoto.__tablename__, []):
        # for compatibility with versions less 0.0.46
        data = item.pop('data', None)
        name = item['id']
        img_path = os.path.join(settings.DISK_PHOTO_DIR, '{}.jpg'.format(name))
        if data:
            kiosk_api.utils.__old_save_img(data, img_path)

        z_alchemy_from_json(alchemy_type=DiskPhoto,
                            json_obj=item,
                            session=request.db_session,
                            cur_time=current_time)

    # save images (for new kiosk versions (>0.0.46))
    if files:
        kiosk_api.utils.save_disk_photo(files.getlist(u'images', []))
    request.db_session.autoflush = True
    request.db_session.commit()


def get_data_to_send(request, current_time):
    data_out = {}
    classes_to_send = [
        Movie, MovieTranslation, MovieMovieGenre, MovieMovieGenre, UPC,
        UpcMovie, UpcSound, UpcSubtitle, User, Card, Disk, Deal, TariffPlan,
        TariffValue, CompanyUpcTariffPlan, FeaturedMovie, VideoFile, Coupon,
        KioskCalibration, KioskSettings, KioskSkipWeekdays, KioskSkipDates,
        Slot, KioskScreens, VideoSchedule, Company, CouponUsageInfo,
        KioskReview, KioskReviewSlot
    ]

    request.db_session.autoflush = False

    for cls in classes_to_send:
        cls_data = request.db_session.query(cls)
        cls_data = cls_data.filter(cls.dt_modify > request.kiosk.dt_sync)
        cls_data = cls_data.filter(cls.dt_modify < current_time)

        for clause in cls.sync_filter_rules:
            cls_data = cls_data.filter(clause(request))

        cls_data = cls_data.all()
        data_out.update(alchemy_list_to_json(cls_data))

    request.db_session.autoflush = True

    return data_out


def ordering(request):
    kiosk = request.kiosk
    s = request.db_session
    slots = s.query(Slot).filter_by(kiosk=kiosk).filter(Slot.status_id == 1).order_by(Slot.number).all()
    if request.kiosk.ordering_list.type_id == 1:
        # order by release date
        disks = s.query(Disk) \
            .join(Slot).filter_by(kiosk=kiosk) \
            .join(Disk.upc).join(UPC.movie).order_by(Movie.dt_release.desc()) \
            .join(Movie.movie_translation).order_by(MovieTranslation.name) \
            .join(UPC.format).order_by(DiskFormat.name.desc()) \
            .order_by(Disk.rf_id).all()
    else:  # if request.kiosk.ordering_list.type_id == 2:
        # Order by Movie name
        disks = s.query(Disk) \
            .join(Slot).filter_by(kiosk=kiosk) \
            .join(Disk.upc).join(UPC.movie) \
            .join(Movie.movie_translation).order_by(MovieTranslation.name) \
            .join(UPC.format).order_by(DiskFormat.name.desc()) \
            .order_by(Disk.rf_id).all()

    disk_to_slot = zip(disks, slots)

    while disk_to_slot:
        disk, slot = disk_to_slot.pop(0)
        if slot.disk != disk:
            if slot.disk:
                empty_slot = kiosk.get_free_slot()
                if empty_slot is None:
                    log.warning("disk: {}, slot: {}, empty_slot: {}".format(disk, slot, empty_slot))
                    continue
                return int(slot.number), int(empty_slot.number)
            else:
                return int(disk.slot.number), int(slot.number)


def get_next_bash_command(request):
    bc = request.db_session.query(KioskBashCommand)\
        .filter(KioskBashCommand.kiosk == request.kiosk)\
        .filter(KioskBashCommand.dt_executed == None)\
        .order_by(KioskBashCommand.id)\
        .first()

    if bc:
        res = {
            'command': 'timeout 20 {}'.format(bc.command),
            'id': int(bc.id)
        }
        bc.send()
    else:
        res = None

    return res
