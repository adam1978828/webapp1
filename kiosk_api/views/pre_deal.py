# -*- coding: utf-8 -*-
import json
from pprint import pprint
import datetime
import sys, traceback

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_POST

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_

from Model import Kiosk, Card, Deal, TariffValue, CouponUsageInfo, Coupon
import WebApp.utils
from WebApp.utils import alchemy_to_json, alchemy_from_json, send_to_admin, get_traceback

# constants for coupon
USER_DECISION = u'user_decision'
COUPON = u'coupon'
DECISION = u'decision'
USES_PER_CARD_LEFT = u'uses_per_card_left'
MESSAGE = u'message'

CARD_EXPIRED_MESSAGE = u'This card is expired, please, use another card'

__author__ = u'D.Ivanets'


@csrf_exempt
@require_POST
def pre_deal(request):
    """
    This function accepts list of deals and credit card credentials.
    It tries to preauthorize required amount and returns result.
    """
    if request.META.get(u'CONTENT_TYPE') == u'application/json':
        json_in = json.loads(request.body)
    else:
        json_in = json.loads(request.POST[u'data'])
    pprint(json_in)
    result = {
        u'error': False,
        u'message': u'OK',
        u'result': False,
        u'attachment': {u'card': None,
                        u'deals': []}
    }
    try:
        assert request.kiosk.company.payment_systems, \
            u'Company does not have any payment accounts'
        assert request.kiosk, u'Kiosk with such uuid does not exists'
        deals = alchemy_from_json(Deal, json_in.get(u'deals', u'[]'))
        assert deals, u'No deals field were in request.'
        assert all(deal.tariff_value_id for deal in deals), \
            u'No tariff value for some deals'
        card = parse_card(request, json_in)
        validate_maximum_rentals(request, deals, card)
        payment_system = request.kiosk.payment_system

        coupon_data = json_in.get(COUPON, None)
        coupon_result = can_use_coupon(deals, request.db_session, card, coupon_data)
        decision = coupon_result.get(DECISION, None)
        if decision is False:
            result[u'error'] = True
            result[COUPON] = coupon_result
            return JsonResponse(result)

        for deal in deals:
            deal.kiosk_start = request.kiosk
            deal.card = card
            deal.payment_account = payment_system
            request.db_session.add(deal)
        request.db_session.commit()

        deals = request.db_session.query(Deal) \
            .filter(Deal.id.in_([deal.id for deal in deals])).all()
        # check and process user decision
        process_user_decision(deals, request.db_session, card, coupon_data)

        if len(deals) > 1:
            amount = 0
            for deal in deals:
                amount += deal.get_preauth_amount()

            auth_result = payment_system.check_amount(card, amount)

            if auth_result.is_approved:
                card.card_status_id = 1

                update_coupon_usage_info(deals, request.db_session)

                for deal in deals:
                    payment_system.preauth_deal(deal)
                auth_result = True
            else:
                card.card_status_id = 1
                for deal in deals:
                    deal.dt_end = deal.dt_start
                    deal.kiosk_end = deal.kiosk_start
                if auth_result.is_card_expired:
                    card.card_status_id = 2
                    for deal in deals:
                        deal.deal_status_id = 403
                    result[u'message'] = CARD_EXPIRED_MESSAGE
                else:
                    for deal in deals:
                        deal.deal_status_id = 404
                    result[u'message'] = u'Could not process your card. ' \
                                         u'Please, Try another one.'
                auth_result = False
        else:
            deal = deals[0]
            res = payment_system.preauth_deal(deal)
            if int(deal.deal_status_id) in (201, 202):

                update_coupon_usage_info(deals, request.db_session)

                auth_result = True
            elif res.is_card_expired:
                auth_result = False
                result[u'message'] = CARD_EXPIRED_MESSAGE
            else:
                auth_result = False
                result[u'message'] = u"Could not process your card. " \
                                     u"Please, use another one."

        result[u'result'] = auth_result
        if auth_result:
            for deal in deals:
                deal.dt_rent_expire = deal.count_dt_expire()
        result[u'attachment'][u'card'] = alchemy_to_json(card)
        result[u'attachment'][u'deals'] = alchemy_to_json(deals)
        request.db_session.commit()
    except AssertionError as ex:
        traceback.print_exc(file=sys.stdout)
        result[u'error'] = True
        result[u'message'] = ex.message
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        result[u'error'] = True
        result[u'message'] = ex.message
        message = get_traceback()
        if not settings.DEBUG:
            send_to_admin(ex, message)
    pprint(result)
    return JsonResponse(result)

def get_percard_and_total_uses_left(deals, card, session):

    deals_with_coupon = [deal for deal in deals if deal.coupon_id]
    # get first deal with coupon
    deal = deals_with_coupon[0]

    coupon_id = deal.coupon_id
    coupon = session.query(Coupon).filter(Coupon.id == coupon_id).first()
    card_id = card.id
    usage_amount = 0

    # check in coupon table
    used_total = coupon.actual_used_total
    coupon_uses_left = coupon.usage_amount - used_total

    # check in coupon_usege_info  table
    coupon_info = session.query(CouponUsageInfo)\
        .filter(and_(CouponUsageInfo.coupon_id==coupon_id,
                     CouponUsageInfo.card_id==card_id)).first()
    if coupon_info:
        usage_amount += coupon_info.usage_amount or 0
    uses_per_card_left = coupon.per_card_usage - usage_amount

    return uses_per_card_left, coupon_uses_left

def get_uses_left(deals, card, session):
    uses_per_card_left, coupon_uses_left = get_percard_and_total_uses_left(deals, card, session)
    uses_left = min([uses_per_card_left, coupon_uses_left])
    return int(uses_left)

def coupon_is_exists(deals, session):
    """
    check is coupon exists in db
    :param deals: deals with coupon
    :return:
    """
    if not deals:
        return None
    else:
        deal = deals[0]
        coupon_id = deal.coupon_id
        coupon = session.query(Coupon).filter(Coupon.id == coupon_id).first()
        return coupon or False

def process_user_decision(deals, session, card, coupon_data):
    deals = [deal for deal in deals if deal.coupon_id]
    if coupon_data:
        user_decision = coupon_data.get(u'user_decision', None)
        if user_decision == u'pass':
            # print 'user_decision == pass'
            uses_left = get_uses_left(deals, card, session)
            deals_without_coupon = deals[uses_left:]
            # delete coupon from overflow deals
            for deal in deals_without_coupon:
                deal.coupon_id = None
                deal.discount = 0
                session.add(deal)
            session.commit()

def can_use_coupon(deals, session, card, coupon_data):
    # coupon, and card must be equal for each deal if it is present in deal
    result = {
        DECISION: None,
        USES_PER_CARD_LEFT: None,
        MESSAGE: None
    }

    uses_per_card_left = None
    deals_with_coupon = [deal for deal in deals if deal.coupon_id]

    if not deals_with_coupon:
        result[DECISION] = True
        result[USES_PER_CARD_LEFT] = uses_per_card_left
        return result

    # check is coupon exist in db
    if coupon_is_exists(deals_with_coupon, session) is False:
        result[DECISION] = False
        result[USES_PER_CARD_LEFT] = uses_per_card_left
        result[MESSAGE] = u'Sorry, but your coupon is unavailable!'
        return result

    if coupon_data:
        user_decision = coupon_data.get(USER_DECISION, None)
        if user_decision == u'pass':
            result[DECISION] = True
            result[USES_PER_CARD_LEFT] = uses_per_card_left
            return result

    uses_per_card_left, coupon_uses_left = get_percard_and_total_uses_left(deals, card, session)

    deal = deals_with_coupon[0]
    coupon_id = deal.coupon_id
    coupon = session.query(Coupon).filter(Coupon.id == coupon_id).first()
    used_total = coupon.actual_used_total
    expect_used_total = used_total + len(deals_with_coupon)
    coupon_amount_less_expected_total = coupon.usage_amount <= expect_used_total
    uses_per_card_left_less_deals = uses_per_card_left < len(deals_with_coupon)
    uses_left = get_uses_left(deals_with_coupon, card, session)

    if uses_per_card_left_less_deals or coupon_amount_less_expected_total:
        result[DECISION] = False
        result[USES_PER_CARD_LEFT] = uses_left
        return result

    result[DECISION] = True
    result[USES_PER_CARD_LEFT] = uses_left
    return result


def update_coupon_usage_info(deals, session):
    for deal in deals:
        coupon_id = deal.coupon_id
        if not (coupon_id is None):
            coupon = session.query(Coupon).filter(Coupon.id == coupon_id).first()
            card_id = deal.card.id
            coupon_info = session.query(CouponUsageInfo)\
                .filter(and_(CouponUsageInfo.coupon_id==coupon_id,
                             CouponUsageInfo.card_id==card_id)).first()
            if not coupon_info:
                coupon_info = CouponUsageInfo(coupon_id=coupon_id,
                                              card_id=card_id)
                session.add(coupon_info)
            coupon_info.refresh_usage_amount()
            coupon.refresh_total_usage()
    session.commit()

def parse_card(request, data_in):
    """
    This function parses card data from request. Kiosk can send full
    information about card like cc_number, cc_expiry, cardholder_name or it
    can send card hash.
    :param request:
    :param data_in:
    :return:
    """
    card_hash = data_in.get(u'card_hash', u'')
    if card_hash:
        # If kiosk sends hash number of card.
        card = request.kiosk.company.get_card_by_hash(card_hash)
        # If there is no card in database with such hash
        assert card, \
            u'Card with such card_hash does not exists'
        # If this card was blocked by company worker or this card
        # was detected in some fraud actions
        assert card.card_status.allow_transaction, \
            u'This card is invalid, please, use another card'
    else:
        # Else if kiosk sends full card information:
        cc_number = data_in.get(u'cc_number', u'')
        cc_expiry = data_in.get(u'cc_expiry', u'')
        cardholder_name = data_in.get(u'cardholder_name', u'')
        assert cc_number and cc_expiry and cardholder_name, \
            u'No card_hash or cc_number, cc_expiry, ' \
            u'cardholder_name field were in request.'
        card = Card()
        card.set_card(cc_number, cc_expiry, cardholder_name)
        card.company_id = request.kiosk.company.id
        try:
            card = request.db_session.query(Card) \
                .filter_by(hash=card.hash) \
                .filter_by(company=request.kiosk.company).one()
        except NoResultFound:
            request.db_session.add(card)
    return card


def validate_maximum_rentals(request, deals, card):
    """Counts number of active rentals. If total number is over maximum,
    raises an error.
    """
    active_rents = request.db_session.query(Deal)\
        .filter(Deal.deal_type_id == 1)\
        .filter(Deal.card == card) \
        .filter(Deal.deal_status_id.in_([301, 311, 201])).count()

    requested_rents = 0

    for deal in deals:
        if deal.deal_type_id == 1:
            requested_rents += 1
    max_rents = int(request.kiosk.settings.max_disks_per_card)

    total_rents = active_rents + requested_rents

    assert not requested_rents or (total_rents <= max_rents), \
        u'The maximum number of disks you can rent is {}, you already ' \
        u'rented {}, so you can not rent {} more. Please, choose ' \
        u'smaller amount of disks for rent.' \
        u''.format(max_rents, active_rents, requested_rents)