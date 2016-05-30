import uuid
import datetime
import re
from django.template.response import TemplateResponse

from Model import Movie, UpcMovie, UPC, Disk, Slot, MovieTranslation, MovieMovieGenre
from Model import MovieGenreTranslation, Kiosk, DiskFormat, ReservationCart, SlotStatus
from Model import Deal, MovieRating
from sqlalchemy import and_, or_, func, distinct
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import sqlalchemy.sql.sqltypes as sqltypes
from libs.utils.coupons_functions import expected_total_rent

from libs.validators.core import json_response_content, validation_error
from libs.validators.string_validators import validate_string_not_empty
from coupons.helpers.processor import CouponProcessor

from ..middleware import cart_item


def kiosks_with_movie(request, movie_id, format_id=None):
    suitable = request.db_session.query(Kiosk)\
        .filter(Kiosk.company_id == request.company.id,
                Kiosk.is_running == True)\
        .join(Slot).join(Disk).join(UPC).join(UpcMovie) \
        .filter(UpcMovie.movie_id == movie_id,
                Slot.status_id == 1,
                Disk.state_id == 0)
    return (suitable.filter(UpcMovie.disk_format_id == format_id) if format_id else suitable).all()


def filter_movies(request, disk_condition):
    category_query = request.GET.get('category', None)
    movies = request.db_session.query(Movie).distinct().join(UpcMovie).join(UPC).join(Disk).join(Slot)
    movies = movies.filter(disk_condition)
    query_string = None
    if category_query:
        query_string = request.GET.get('query', None)
    # print category_query, query_string
    if category_query and query_string:
            if category_query == u'genre':
                request.db_session.query()
                movies = process_genre(query_string, movies)
            elif category_query == u'title':
                movies = process_title(query_string, movies)
            elif category_query == u'year':
                movies = process_year(query_string, movies)
            elif category_query == u'rating':
                movies = process_rating(query_string, movies)
    # movies = movies.group_by(Movie.id).order_by(func.min(Disk.state_id), Movie.id)
    return movies

def process_genre(query_string, movies):
    movies = movies.join(MovieMovieGenre).join(MovieGenreTranslation, MovieMovieGenre.movie_genre_id == MovieGenreTranslation.movie_genre_id)\
        .filter(MovieGenreTranslation.value == query_string)
    return movies

def process_title(query_string, movies):
    movies = movies.join(MovieTranslation)
    if query_string == 'normal':
        movies = movies.order_by(MovieTranslation.name)
    else:
        movies = movies.order_by(MovieTranslation.name.desc())
    return movies

def process_year(query_string, movies):
    if query_string == 'normal':
        movies = movies.join(Movie).order_by(Movie.release_year, Movie.dt_dvd_release)
    else:
        movies = movies.join(Movie).order_by(Movie.release_year.desc(), Movie.dt_dvd_release.desc())
    return movies

def process_rating(query_string, movies):
    value = query_string
    movies = movies.join(MovieRating).filter(MovieRating.value == value)#.order_by(MovieRating.value)
    return movies

def check_availability(request, upc, kiosk_id):
    return bool(request.db_session.query(Disk).join(Slot).filter(and_(
                Disk.state_id == 0, Slot.kiosk_id == kiosk_id, Disk.upc_link == upc
                )).count())


def change_cart_kiosk(request, kiosk_id):
    if request.user.is_authenticated():
        for item in request.items:
            item.kiosk_id = kiosk_id
            item.is_available = check_availability(request, item.upc.upc, kiosk_id)
            request.db_session.add(item)
        request.db_session.commit()
        if request.preferred_kiosk:
            for item in request.items:
                item.actual_tariff_value = item.upc.get_tariff_value(request.preferred_kiosk)
    else:
        request.session['cart'] = [cart_item(x['upc'], kiosk_id, x['format_id'], 
            check_availability(request, x['upc'], kiosk_id)) for x in request.session['cart']]
        # just stub for now - think of more elegant solution
        request.items = [
            {
                'upc': request.db_session.query(UPC)
                              .filter_by(upc=d['upc']).first(),
                'kiosk': request.db_session.query(Kiosk)
                                .filter_by(id=d['kiosk_id']).first(),
                'disk_format': request.db_session.query(DiskFormat)
                                      .filter_by(id=d['format_id'])
                                      .first(),
                'is_available': d['is_available'],
            } for d in request.session['cart']]
        if request.preferred_kiosk:
            for item in request.items:
                item['actual_tariff_value'] = item['upc'].get_tariff_value(request.preferred_kiosk)


def change_preferred_kiosk(request, kiosk_id):
    request.session['preferred_kiosk'] = int(kiosk_id) if kiosk_id is not None else kiosk_id
    change_cart_kiosk(request, kiosk_id)
    request.session.modified = True
    request.preferred_kiosk = request.db_session.query(Kiosk).filter_by(id=kiosk_id).first()


def approve_reservations(request):
    items = request.db_session.query(ReservationCart).filter_by(user_id=request.user.id)\
        .filter_by(is_available=True).filter_by(is_reserved=False).all()
    unique_code = str(uuid.uuid4())[:8]
    response, deals = json_response_content(), []
    kiosk, card = request.preferred_kiosk, request.card
    
    for item in items:
        query = request.db_session.query(Disk).join(Slot).join(SlotStatus)\
            .filter(and_(Disk.upc_link == item.upc_link,
                         Disk.state_id == 0,
                         Slot.kiosk_id == item.kiosk_id,
                         SlotStatus.id == 1))
        try:
            disk = query.one()
        except NoResultFound:
            response['type'] = 'warning'
            response['errors'].append(validation_error(item.upc.upc, 'Disk is already reserved or ejected'))
            print "No disk with such params"
            continue
        except MultipleResultsFound:
            disk = query.first()
            print disk
        except Exception, e:
            response['type'] = 'warning'
            response['errors'].append(validation_error(item.upc.upc, e.message))
            print e
            continue

        deal = Deal()
        deal.card = card
        deal.coupon = item.coupon
        deal.deal_status_id = 231
        deal.deal_type_id = 1
        deal.dt_start = datetime.datetime.utcnow()
        deal.dt_reservation_expire = datetime.datetime.utcnow() + \
            datetime.timedelta(minutes=int(kiosk.settings.reservation_expiration_period))
        # Do both, because it might be used by other methods and before
        # session.commit() deal.disk without deal.rf_id is invalid
        deal.disk = disk
        deal.rf_id = disk.rf_id
        disk.state_id = 9
        deal.secret_code = unique_code
        deal.tariff_value = disk.upc.get_tariff_value(kiosk)
        deal.kiosk_start = kiosk

        if deal.no_errors():
            request.db_session.add_all([deal, disk])
            same_disks_in_cart = request.db_session.query(ReservationCart)\
                .filter(ReservationCart.upc_link == item.upc_link,
                    ReservationCart.kiosk_id == item.kiosk_id,
                    ReservationCart.disk_format_id == item.disk_format_id).all()
            for disk in same_disks_in_cart:
                disk.is_reserved = True
            request.items.remove(item)
            request.db_session.add_all(same_disks_in_cart)
            deals.append(deal)
            if not response['type']:
                response['type'] = 'success'
                response['message'] = 'All disks were successfully reserved'
        else:
            response['type'] = 'error'
            for error in deal.errors:
                response['errors'].append(validation_error(item.upc.upc, error['message']))
    
    preauth_success, feedback = preauthorize_reservation_deals(card, kiosk, deals)
    
    if preauth_success:
        for item in items:
            request.db_session.delete(item)
        if not feedback:
            response['type'] = 'info'
        # if deals[0].coupon:
        #     cp = CouponProcessor(deals[0].coupon)
        #     cp.discount(deals)
        items = request.db_session.query(ReservationCart).filter_by(user_id=request.user.id)\
            .filter_by(is_reserved=False).all()
        empty_slots = int(request.preferred_kiosk.settings.max_disks_per_card) - len(items)
        disks_data = map(lambda x: (x.upc, x.kiosk, x.is_available, x.discount), request.items)
        items = map(lambda x: not x.is_available, items)
        request.items = items
        html = TemplateResponse(request, 'site/reservation/ajax_cart.html',
            {'empty_slots': [None]*empty_slots, 'not_available_items': any(items),
                'payments': expected_total_rent(disks_data), 'valid_card': preauth_success,
                'successfull_reservation': True})
        html.render()
        request.db_session.commit()
        response['data'] = {
            'cartTemplate': html.content,
            'disks_amount': len(items),
            'secret_code': unique_code
        }
    else:
        response['type'] = 'error'
        response['message'] = feedback['message']
        request.db_session.expunge_all()  
    return response


def preauthorize_reservation_deals(card, kiosk, deals):
    payment_system = kiosk.payment_system.system
    result = {
        u'error': False,
        u'message': u'OK',
        u'result': False,
        u'attachment': {
            'card': None,
            'deals': []
        }
    }

    for deal in deals:
        deal.payment_account = kiosk.payment_system

    if len(deals) > 1:
        amount = 0
        for deal in deals:
            amount += deal.get_preauth_amount()

        auth_result = payment_system.check_amount(card, amount or 0.1)
        if auth_result.get(u'TransactionResult') == u'APPROVED':
            card.card_status_id = 1
            for deal in deals:
                payment_system.preauth_deal(deal)
            auth_result = True
        else:
            if auth_result.get(u'ErrorMessage') in [u'Credit card is expired.']:
                card.card_status_id = 2
                for deal in deals:
                    deal.deal_status_id = 403
                    deal.dt_end = deal.dt_start
                    deal.kiosk_end = deal.kiosk_start
                result[u'message'] = u'This card is invalid, please, use another card'
            elif auth_result.get(u'ErrorMessage', None):
                for deal in deals:
                    if u'credit card' in auth_result[u'ErrorMessage'].lower():
                        deal.card.card_status_id = 2
                    else:
                        deal.card.card_status_id = 1
                    deal.deal_status_id = 404
                    deal.dt_end = deal.dt_start
                    deal.kiosk_end = deal.kiosk_start
                result['message'] = auth_result[u'ErrorMessage']
            elif auth_result.get('faultstring') == u'MerchantException':
                for deal in deals:
                    deal.card.card_status_id = 2
                    deal.deal_status_id = 404
                    deal.dt_end = deal.dt_start
                    deal.kiosk_end = deal.kiosk_start
                result['message'] = 'Invalid card'
            else:
                for deal in deals:
                    card.card_status_id = 1
                    deal.deal_status_id = 404
                    deal.dt_end = deal.dt_start
                    deal.kiosk_end = deal.kiosk_start
                result[u'message'] = u'Could not process your card. Please, Try another one.'
            auth_result = False
    elif len(deals) == 1:
        deal = deals[0]
        result = payment_system.preauth_deal(deal)
        if int(deal.deal_status_id) in (201, 202, 241):
            auth_result = True
        else:
            auth_result = False
    else:
        auth_result, result = True, None
    return (auth_result, result)
