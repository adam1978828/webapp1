# -*- coding: utf-8 -*-
from json import loads

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from Model import Kiosk, Slot
from Model.ordering_list import OrderingList
from Model import KioskReview, KioskReviewSlot, KioskAction

from libs.validators.core import json_response_content
from acc.decorators import permission_required

from datatables import ColumnDT, DataTables


@login_required
@permission_required('kiosk_view')
def kiosk_slots(request, kiosk_id):
    slots = request.db_session.query(Slot).filter_by(kiosk_id=kiosk_id).order_by(Slot.number)
    rack1 = slots.filter((101 <= Slot.number) & (Slot.number <= 170)).all()
    rack2 = slots.filter((228 <= Slot.number) & (Slot.number <= 270)).all()
    rack3 = slots.filter((501 <= Slot.number) & (Slot.number <= 570)).all()
    rack4 = slots.filter((601 <= Slot.number) & (Slot.number <= 670)).all()

    curr_review = request.db_session.query(KioskReview).filter(KioskReview.kiosk_id == kiosk_id, KioskReview.dt_end == None).first()
    if curr_review:
        reviewed = [slot.slot.id for slot in curr_review.review_slots.filter(KioskReviewSlot.dt_check != None).all()]
        in_review_list = [slot.slot.id for slot in curr_review.review_slots.filter(KioskReviewSlot.dt_check == None).all()]
    else:
        reviewed = []
        in_review_list = []

    return render(request, 'kiosk_slots.html',
                  {'racks': [rack1, rack2, rack3, rack4],
                   'kiosk': request.db_session.query(Kiosk).filter_by(id=kiosk_id).first(),
                   'curr_review': curr_review,
                   'reviewed': reviewed,
                   'in_review_list': in_review_list,
                   })


@login_required
@require_POST
def ajax_review_inventory(request, kiosk_id, review_type_id):

    kiosk = request.db_session.query(Kiosk).get(kiosk_id)
    result = put_inventory_in_db(request, kiosk, review_type_id)

    return JsonResponse(json_response_content(**result))


def put_inventory_in_db(request, kiosk, review_type_id=1, load_db=False):
    if kiosk.active_review_inventory:
        return {'response_type': 'success',
                'msg': 'Review on kiosk #{id}//{name} has been already started!'.
                    format(id=kiosk.id, name=kiosk.settings.alias)}
    slots = None
    if int(review_type_id) == 2:
        slots = loads(request.POST['slots'])
        if not slots:
            return {'response_type': 'error', 'msg': 'No slots specified!'}

    action = KioskAction(kiosk_id=kiosk.id, user_id=request.user.id, action_id=3)
    review = KioskReview(kiosk_id=kiosk.id, user_id=request.user.id, type_id=review_type_id)
    review.load_db = load_db

    request.db_session.add(action)
    request.db_session.add(review)

    request.db_session.commit()

    create_review_slot(request, review, review_type_id, slots)

    return {'response_type': 'success',
            'msg': 'Review on kiosk #{id}//{name} was activated!'.
                format(id=kiosk.id, name=kiosk.settings.alias)}


def create_review_slot(request, review, review_type_id, slots):
    if int(review_type_id) == 2:
        for slot in slots:
            review_slot = KioskReviewSlot(review_id=review.id, slot_id=int(slot))
            request.db_session.add(review_slot)
    else:
        reviews = [KioskReviewSlot(review=review, slot=slot)
                   for slot in review.kiosk.slots]
        request.db_session.add_all(reviews)

    request.db_session.commit()


@login_required
@require_POST
def ajax_review_kill(request, kiosk_id, review_id):
    review = request.db_session.query(KioskReview).filter(KioskReview.kiosk_id == kiosk_id, KioskReview.id == review_id).first()
    review and review.kill()
    return JsonResponse(json_response_content('success', 'Review was canceled!'))


@login_required
def ajax_review_all(request, kiosk_id):

    def _unknown_column_value(val):
        return val if val is not None else '-'

    def _date_time_column(val):
        return val.strftime('%m/%d/%y %I:%M %p') if val is not None else '-'

    def _get_slot_number(val):
        return val.slot.number if val else '-'

    def _get_user_name(val):
        return val.full_name if val else '-'

    columns = list()
    columns.append(ColumnDT('id'))
    columns.append(ColumnDT('kiosk_id', filter=_unknown_column_value))
    columns.append(ColumnDT('dt_start', filter=_date_time_column))
    columns.append(ColumnDT('dt_end', filter=_date_time_column))
    columns.append(ColumnDT('dt_break', filter=_date_time_column))
    columns.append(ColumnDT('checked_total', filter=_unknown_column_value))
    columns.append(ColumnDT('last_slot', filter=_get_slot_number))
    columns.append(ColumnDT('user', filter=_get_user_name))

    query = request.db_session.query(KioskReview).filter(KioskReview.kiosk_id == kiosk_id)
    row_table = DataTables(request, KioskReview, query, columns)
    response = row_table.output_result()
    return JsonResponse(response)


@login_required
# @require_POST
def ajax_disk_to_eject(request, slot_id, is_to_eject):
    slot = request.db_session.query(Slot).get(slot_id)
    if not slot:
        raise Http404
    # If we want to eject this disk
    if int(is_to_eject):
        if slot.status_id == 1:
            if slot.disk and slot.disk.state_id == 0:
                slot.status_id = 7
                slot.disk.state_id = 8
            else:
                raise Http404
        elif slot.status_id == 5:
            slot.status_id = 7
        else:
            raise Http404
        status = 'To eject'
    else:
        if slot.status_id == 7:
            if slot.disk:
                slot.status_id = 1
                slot.disk.state_id = 0
                status = 'Occupied'
            else:
                slot.status_id = 5
                status = 'No rfid'
        else:
            raise Http404
    response = json_response_content('success',
                                     'Success',
                                     data={'status': status,
                                           'button': render_to_string('slot_button.html',
                                                                      {'slot': slot})})
    request.db_session.commit()
    return JsonResponse(response)


@login_required
@require_POST
def ajax_order_by(request, kiosk_id, order_type_id):
    kiosk = request.db_session.query(Kiosk).get(kiosk_id)
    if kiosk.ordering_list:
        request.db_session.delete(kiosk.ordering_list)
    kiosk.ordering_list = OrderingList(type_id=order_type_id)
    request.db_session.commit()
    return JsonResponse(json_response_content('success', 'Sorting was successfully activated'))