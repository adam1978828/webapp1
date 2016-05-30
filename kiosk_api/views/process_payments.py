# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import or_

from libs.utils.list_functions import partition_by
from coupons.helpers.processor import CouponProcessor
from Model import *


__author__ = 'D.Ivanets, D.Kalpakchi'

# TODO: properly save transaction result after each transaction!
# => ...


@csrf_exempt
def process_payments(request):
    request.current_time = datetime.datetime.utcnow()

    grace_change_status(request)
    request.db_session.commit()

    server_error_change_status(request)
    request.db_session.commit()

    process_over_rented(request)
    request.db_session.commit()

    process_grace(request)
    request.db_session.commit()

    process_over_reserved(request)
    request.db_session.commit()

    process_offline_rents(request)
    request.db_session.commit()

    process_closed_rents(request)
    request.db_session.commit()

    process_purchases(request)
    request.db_session.commit()

    process_manually_reverted_purchases(request)
    request.db_session.commit()

    return JsonResponse({})


def process_offline_rents(request):
    """This view looks for offline rentals and pre_authorizes required amount
    from customer card.
    """
    # 321, "NA EJECTED RENT"
    deals_offline = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id == 321)\
        .all()

    for deal in deals_offline:
        deal.ps_preauth()
        request.db_session.commit()


def grace_change_status(request):
    """
    Change status of deals if grace period expired
    """
    # 301, "G EJECTED RENT"
    # 302, "G EJECTED SALE"

    deals_grace = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id.in_((301, 302))).all()

    status_map = {
        301: 311,  # 311, "EJECTED RENT"
        302: 312,  # 312, "EJECTED SALE"
    }

    for deal in deals_grace:

        grace_period = deal.kiosk_start.settings.grace_period
        grace_period = datetime.timedelta(minutes=int(grace_period))
        deal_started = deal.dt_start
        last_sync = deal.kiosk_start.dt_sync
        now = request.current_time

        if now - deal_started > grace_period:
            if last_sync - deal_started > grace_period:
                deal.deal_status_id = status_map[int(deal.deal_status_id)]
        request.db_session.commit()
    request.db_session.commit()


def server_error_change_status(request):
    """
    Changes NEW deals to Error after 30 minutes of server fail.
    """
    filter_date = request.current_time - datetime.timedelta(minutes=30)
    # 101, "NEW RENT"
    # 102, "NEW SALE"
    deals_error = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id.in_((101, 102))) \
        .filter(Deal.dt_start < filter_date).all()

    for deal in deals_error:
        deal.deal_status_id = 450  # 450, "SERVER ERROR"
        request.db_session.commit()

    request.db_session.commit()


def process_closed_rents(request):
    """
    Process all rental deals where disk was already returned
    """

    deals_rent = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id.in_((511, 521, 531, 701))) \
        .filter(or_(Deal.dt_next_retry.is_(None),
                    Deal.dt_next_retry <= request.current_time)) \
        .all()
    status_map = {
        511: 601,
        521: 621,
        531: 641,
        701: 621,
    }

    for deal in deals_rent:
        if deal.deal_status_id != 701:
            deal.total_days = deal.count_rental_period()
            if not deal.force_total_amount:
                deal.total_amount = deal.calculate_amount()

        deal.payment_system.process_amount_for_deal(deal)
        request.db_session.commit()
        
        if deal.is_fully_charged():

            deal.deal_status_id = status_map[deal.deal_status_id]
            deal.dt_next_retry = None
        else:
            delta = deal.kiosk_start.retry_delta()
            deal.dt_next_retry = request.current_time + delta
        request.db_session.commit()


def process_purchases(request):
    """
    Process all purchases with grace period expired.
    @params
    """
    # 312, "EJECTED SALE"       602,"CLOSED SALE"
    # 322, "NA EJECTED SALE"    602,"CLOSED SALE"
    # 702, "M CHANGED SALE"     622,"M CLOSED SALE"
    # 712, "CONVERTED SALE"     632,"CONV CLS SALE"

    deals_sale = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id.in_((312, 322, 702, 712))) \
        .filter(or_(Deal.dt_next_retry.is_(None),
                    Deal.dt_next_retry <= request.current_time)) \
        .all()
    status_map = {312: 602,
                  322: 602,
                  702: 622,
                  712: 632}
    for deal in deals_sale:
        if not deal.force_total_amount:
            deal.total_amount = deal.calculate_amount()
        deal.payment_system.process_amount_for_deal(deal)
        request.db_session.commit()

        if deal.is_fully_charged():

            deal.deal_status_id = status_map[deal.deal_status_id]
            deal.dt_next_retry = None
        else:
            delta = deal.kiosk_start.retry_delta()
            deal.dt_next_retry = request.current_time + delta
        request.db_session.commit()


def process_manually_reverted_purchases(request):
    """
    Process all purchases that was manually marked as 'need revert'.
    All that deals of type sale with status 522.
    @params
    """
    deals_sale = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id == 522)\
        .filter(or_(Deal.dt_next_retry.is_(None),
                    Deal.dt_next_retry <= request.current_time)) \
        .all()
    for deal in deals_sale:
        deal.total_amount = 0
        deal.payment_system.process_amount_for_deal(deal)
        request.db_session.commit()
        # deal.deal_status_id = 622

        if deal.is_fully_charged():

            deal.deal_status_id = 622
            deal.dt_next_retry = None
        else:
            delta = deal.kiosk_start.retry_delta()
            deal.dt_next_retry = request.current_time + delta


def process_over_rented(request):
    # EJECTED RENT: 311
    rents = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id == 311) \
        .filter(Deal.dt_rent_expire.isnot(None)) \
        .filter(Deal.dt_rent_expire < request.current_time) \
        .all()

    for deal in rents:
        deal.deal_type_id = 2
        deal.dt_end = deal.dt_rent_expire
        deal.total_amount = float(deal.tariff_value.sale) * (1 + 0.01 * float(deal.kiosk_start.settings.sale_tax_rate))
        deal.deal_status_id = 712
        deal.disk.state_id = 4
        request.db_session.add_all([deal, deal.disk])
        request.db_session.commit()
    request.db_session.commit()


def process_over_reserved(request):
    # TODO: change it to capture
    # PREAUTH RESERVED: 241
    rents = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id == 241) \
        .filter(Deal.dt_reservation_expire.isnot(None)) \
        .filter(Deal.dt_reservation_expire < request.current_time) \
        .all()

    # Can be done with OVER window fn.
    # E.g.: s.query(func.min(Deal.id).over(partition_by='secret_code'))\
    #           .filter(Deal.secret_code.isnot(None)).all()
    # But it depends on db, so if we change db, that code won't work. That's why:
    rents = partition_by(rents, 'secret_code')

    for group in rents:
        if group[0].coupon:
            cp = CouponProcessor(group[0].coupon)
            cp.discount(group)
        for deal in group:
            deal.dt_end = deal.dt_reservation_expire
            deal.deal_status_id = 531
            deal.disk.state_id = 0
            request.db_session.add_all([deal, deal.disk])
            request.db_session.commit()
        request.db_session.commit()
    request.db_session.commit()


def process_grace(request):
    # 501: G RETURNED RENT:
    # 502: G RETURNED SALE:
    # 420: CANNOT EJECT:
    # 440: NOT PICKED:
    # 460: KAPP DOWN:
    deals_grace = request.db_session.query(Deal) \
        .filter(Deal.deal_status_id.in_((501, 502, 420, 440, 460)))\
        .filter(or_(Deal.dt_next_retry.is_(None),
                    Deal.dt_next_retry <= request.current_time)) \
        .all()
    for deal in deals_grace:
        deal.total_amount = 0
        deal.payment_system.process_amount_for_deal(deal)
        request.db_session.commit()

        if deal.is_fully_charged():
            status_map = {
                501: 611,
                502: 612,
                420: 620,
                440: 640,
                460: 660,
            }
            deal.deal_status_id = status_map[deal.deal_status_id]
        else:
            delta = deal.kiosk_start.retry_delta()
            deal.dt_next_retry = request.current_time + delta
        request.db_session.commit()
