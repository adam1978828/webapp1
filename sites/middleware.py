from Model import ReservationCart, UPC, Kiosk, DiskFormat, Card, Movie
from coupons.helpers.processor import CouponProcessor

__author__ = 'D.Kalpakchi, D.Ivanets'


def cart_item(upc, kiosk_id, format_id, discount, is_available=True):
    return {
        'upc': upc,
        'kiosk_id': int(kiosk_id),
        'format_id': format_id,
        'is_available': is_available,
        'discount': discount or 0
    }


class ReservationMiddleware(object):
    def process_request(self, request):
        kiosk_id = request.session.get('preferred_kiosk', -1)
        k = request.db_session.query(Kiosk) \
            .filter_by(id=kiosk_id).first()
        request.preferred_kiosk = k

        if request.user.is_authenticated():
            user_cart = request.db_session.query(ReservationCart)\
                .filter_by(user_id=request.user.id)
            request.items = user_cart.filter_by(is_reserved=False).all()
            reserved_in_cart = user_cart.filter_by(is_reserved=True).all()
            request.already_reserved_items = ", ".join(map(lambda x: x.upc.movie.get_name, 
                reserved_in_cart))
            request.movies_in_cart = map(lambda x: x.upc_link, request.items)
            request.card = request.db_session.query(Card)\
                .filter_by(id=request.session.get('card_id', '')).first()
            if request.items and request.items[0].coupon:
                cp = CouponProcessor(request.items[0].coupon)
                cp.expected_discount(request.items)
            if request.preferred_kiosk:
                for item in request.items:
                    item.actual_tariff_value = item.upc.get_tariff_value(request.preferred_kiosk)
        else:
            # this guy filters cart for repetitive upc
            cart = {i['upc']: i for i in request.session.get('cart', [])}
            request.session['cart'] = cart.values()
            request.items = [
                {
                    'upc': request.db_session.query(UPC)
                        .filter_by(upc=d['upc']).first(),
                    'kiosk': request.db_session.query(Kiosk)
                        .filter_by(id=d['kiosk_id']).first(),
                    'disk_format': request.db_session.query(DiskFormat)
                        .filter_by(id=d['format_id']).first(),
                    'is_available': d['is_available'],
                    'discount': d.get('discount', 0)
                } for d in request.session['cart']]
            if request.preferred_kiosk:
                for item in request.items:
                    item['actual_tariff_value'] = item['upc'].get_tariff_value(request.preferred_kiosk)
            request.movies_in_cart = map(lambda x: x['upc'].upc, request.items)
        request.last_found_movies = map(lambda x: request.db_session.query(Movie).filter_by(id=x).first(), 
            request.session.get('last_search', []))


    def process_response(self, request, response):
        # NOTE: We can not do this here!!!!
        # Because, during ajax, response is also processed and cart is not saved!
        # if not request.user.is_authenticated():
        #     new_cart = [{'upc': item['upc'].upc,
        #                  'kiosk_id': int(item['kiosk'].id),
        #                  'format_id': int(item['disk_format'].id),
        #                  'is_available': item['is_available']}
        #                 for item in request.items]
        #     print new_cart, request.session['cart']
        #     if new_cart != request.session['cart']:
        #         request.session['cart'] = new_cart
        #         request.session.modified = True
        return response