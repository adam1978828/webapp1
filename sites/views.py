from operator import itemgetter
from django.conf import settings

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core import mail
from django.contrib import auth
from django.views.decorators.http import require_POST, require_GET
from django.core.validators import ValidationError
from django.utils.decorators import decorator_from_middleware

from .helpers.view_helpers import *

from Model import FeaturedMovie, Card, User, UserRestorePassword, Coupon, UserConfirmationEmail
from WebApp.utils import alchemy_to_json
from middleware import ReservationMiddleware

from libs.utils.paginator import Paginator, EmptyPage
from coupons.helpers.processor import CouponProcessor
from datetime import date, datetime
import hashlib, re, random


def sites_global(request):
    """A context processor that provides global vars for views of this app"""
    genres = request.db_session.query(MovieGenreTranslation.value).filter_by(language_id=1).all()
    genres = map(itemgetter(0), genres)
    ratings = request.db_session.query(MovieRating.value).all()
    ratings = map(itemgetter(0), ratings)
    return {
        'genres': genres,
        'ratings': ratings,
    }

def user_is_authenticated(request):
    if not request.user.is_authenticated():
        raise Http404


def page_for_logout_user(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('sites.views.personal_data'))
    return ''

@decorator_from_middleware(ReservationMiddleware)
def index(request):
    featured = request.db_session.query(Movie)\
        .outerjoin(FeaturedMovie)\
        .join(UpcMovie).join(UPC).join(Disk)\
        .filter(Disk.company_id == request.company.id)\
        .outerjoin(Slot) \
        .filter(and_(or_(FeaturedMovie.company_id == request.company.id,
                         FeaturedMovie.company_id == None),
                     or_(FeaturedMovie.is_active == True,
                         FeaturedMovie.is_active == None),
                     Disk.state_id == 0))\
        .join(Slot.kiosk).filter(Kiosk.is_running == True)
    if request.preferred_kiosk:
        featured = featured.filter(Slot.kiosk_id == request.preferred_kiosk.id)
    featured = featured.group_by(Movie.id)\
        .order_by(func.min(Movie.release_year).desc(), 
                  func.bool_and(FeaturedMovie.is_active),
                  func.min(FeaturedMovie.dt_modify))\
        .limit(6)
    movies = request.db_session.query(Movie).distinct()\
        .join(UpcMovie).join(UPC)\
        .join(Disk).join(Slot)\
        .filter(and_(Disk.company_id == request.company.id,
                     Disk.state_id.in_([0, 3]),
                     Slot.status_id == 1
                     ))\
        .join(Slot.kiosk).filter(Kiosk.is_running == True) \
        .order_by(Disk.state_id)
    random_list_id_movies = list(map((lambda x: x.id), (list(movies.limit(10)))))
    random.shuffle(random_list_id_movies)
    return render_to_response('site/main.html', {
        'featured': featured,
        'random_list_id_movies': random_list_id_movies,
        'movies': movies.limit(10)
    }, context_instance=RequestContext(request, processors=[sites_global]))


@decorator_from_middleware(ReservationMiddleware)
def movie_details(request, movie_id):
    movie = request.db_session.query(Movie).filter_by(id=movie_id).first()
    suitable_kiosks = kiosks_with_movie(request, movie_id)
    return render_to_response('site/movieinfo/movie_info.html', {
        'kiosks': [[k.settings.alias.encode('utf-8'),
                    k.address.latitude or '',
                    k.address.longitude or '',
                    reverse('sites.views.specific_kiosk', args=(k.id,), urlconf='sites.urls'),
                    k.address.to_string().encode('utf-8')
                    ] for k in suitable_kiosks],
        'movie': movie
    }, context_instance=RequestContext(request, processors=[sites_global]))


@require_GET
@decorator_from_middleware(ReservationMiddleware)
def movies_search(request):
    per_page = int(request.GET.get('perPage', 10))
    page = int(request.GET.get('page', 1))
    infinite = request.GET.get('inf', False)

    movies = filter_movies(request, and_(
        Disk.company_id == request.company.id,
        Disk.state_id == 0,
        Slot.status_id == 1
    ))

    request.session['last_search'] = map(lambda x: int(x.id), movies)
    request.session.modified = True

    # return it from filter_movies later
    # query = request.GET.get('query', None)
    category = request.GET.get('category', None)

    if infinite:
        return render_to_response('site/partials/movie_info_list.html', {
            'movies': movies.offset(per_page * (page - 1)).limit(per_page),
            'page': page
        }, context_instance=RequestContext(request, processors=[sites_global]))
    else:
        return render_to_response('site/movielist/movie_list.html', {
            'search_category': category,
            'movies': movies.offset(per_page * (page - 1)).limit(per_page),
            'multiple_pages': movies.count() > per_page
            # 'pages': cur_page.indented(5),
            # 'current': cur_page,
        }, context_instance=RequestContext(request, processors=[sites_global]))


@decorator_from_middleware(ReservationMiddleware)
def contacts(request):
    return render_to_response('site/contacts/contacts.html', {
            'company': [[request.company.name.encode('utf-8'),
                    request.company.address.latitude or '',
                    request.company.address.longitude or '',
                    '',
                    request.company.address.to_string().encode('utf-8'),
                    request.company.address.city.encode('utf-8'),
                    request.company.address.state.encode('utf-8'),
                    request.company.address.postalcode.encode('utf-8')
                ]]
        }, 
        context_instance=RequestContext(request, processors=[sites_global]))


@require_GET
@decorator_from_middleware(ReservationMiddleware)
def company_kiosks(request):
    return render_to_response('site/kioskmap/kioskmap.html', {
        'kiosks': [[k.settings.alias.encode('utf-8'),
                    k.address.latitude or '',
                    k.address.longitude or '',
                    reverse('sites.views.specific_kiosk', args=(k.id,), urlconf='sites.urls'),
                    k.address.line_1.encode('utf-8'),
                    k.address.city.encode('utf-8'),
                    k.address.state.encode('utf-8'),
                    k.address.postalcode.encode('utf-8')
                    ] for k in request.company.active_kiosks],
    }, context_instance=RequestContext(request, processors=[sites_global]))


@require_GET
@decorator_from_middleware(ReservationMiddleware)
def specific_kiosk(request, kiosk_id):
    per_page = int(request.GET.get('perPage', 10))
    page = int(request.GET.get('page', 1))
    infinite = request.GET.get('inf', False)
    kiosk = request.db_session.query(Kiosk).filter_by(company_id=request.company.id) \
        .filter_by(id=kiosk_id).filter_by(is_running=True).first()

    if kiosk:
        kiosk_genres = request.db_session.query(MovieGenreTranslation.value)\
            .distinct(MovieGenreTranslation.value) \
            .join(MovieMovieGenre, MovieGenreTranslation.movie_genre_id == MovieMovieGenre.movie_genre_id) \
            .join(UpcMovie, MovieMovieGenre.movie_id == UpcMovie.movie_id) \
            .join(Disk, UpcMovie.upc == Disk.upc_link) \
            .join(Slot, Disk.slot_id == Slot.id) \
            .filter(and_(Slot.kiosk_id == kiosk_id,
                         Slot.status_id == 1))\
            .filter(MovieGenreTranslation.language_id == 1).all()
        kiosk_genres = map(itemgetter(0), kiosk_genres)
        kiosk_ratings = request.db_session.query(MovieRating.value)
        kiosk_ratings = map(itemgetter(0), kiosk_ratings)

        kiosk_info = [[kiosk.settings.alias.encode('utf-8') if kiosk.settings else "Kiosk",
                       kiosk.address.latitude or '',
                       kiosk.address.longitude or '',
                       reverse('sites.views.specific_kiosk', args=(kiosk.id,), urlconf='sites.urls'),
                       kiosk.address.to_string().encode('utf-8'),
                       kiosk.address.city.encode('utf-8'),
                       kiosk.address.state.encode('utf-8'),
                       kiosk.address.postalcode.encode('utf-8')
                       ]]

        movies = filter_movies(request, and_(Slot.kiosk_id == kiosk_id, Disk.state_id == 0, Slot.status_id == 1))
        query = request.GET.get('query', None)
        category = request.GET.get('category', None)
        if infinite:
            return render_to_response('site/partials/movie_info_list.html', {
                'movies': movies.offset(per_page * (page - 1)).limit(per_page),
                'page': page
            }, context_instance=RequestContext(request, processors=[sites_global]))
        else:
            if query and category:
                return render_to_response('site/movielist/movie_list.html', {
                    'search_category': category,
                    'movies': movies.offset(per_page * (page - 1)).limit(per_page),
                    'multiple_pages': movies.count() > per_page
                }, context_instance=RequestContext(request, processors=[sites_global]))
            else:
                return render_to_response('site/kioskdiscs/kioskdiscs.html', {
                    'search_by': query if category == 'genre' else None,
                    'kiosk': kiosk,
                    'kiosk_info': kiosk_info,
                    'kiosk_genres': kiosk_genres,
                    'kiosk_ratings': kiosk_ratings,
                    'movies': movies.offset(per_page * (page - 1)).limit(per_page),
                    'multiple_pages': movies.count() > per_page
                }, context_instance=RequestContext(request, processors=[sites_global]))
    else:
        return render(request, 'site/404.html', {'message': "No kiosk found"})


@decorator_from_middleware(ReservationMiddleware)
def login(request):
    if request.user.is_authenticated():
        response = json_response_content('success', "You've already authenticated")
    else:
        if request.method == "POST":
            email = request.POST.get('email', u'')
            password = request.POST.get('password', u'')
            auth_errors = []

            user_temp = request.db_session.query(User) \
                .filter_by(email=email.strip().lower()) \
                .filter_by(is_email_valid=False) \
                .filter_by(user_type_id=1)\
                .filter_by(company_id=request.company.id) \
                .first()
            if user_temp:
                response = json_response_content('info', "Send email again")
                response['data'] = {'send_email_again': email}
                return JsonResponse(response)

            try:
                validate_string_not_empty(email)
            except ValidationError, e:
                auth_errors.append(validation_error('email', "Email can't be empty"))

            try:
                validate_string_not_empty(password)
            except ValidationError, e:
                auth_errors.append(validation_error('password', "Password can't be empty"))

            if not auth_errors:
                user = auth.authenticate(username=email,
                                         password=password,
                                         user_type=[1],
                                         company_id=request.company.id,
                                         errors=auth_errors)

                if user is not None:
                    if user.is_active:
                        auth.login(request, user)
                        preferred = request.preferred_kiosk
                        request.session['preferred_kiosk'] = int(preferred.id) if preferred else None
                        request.session.modified = True
                        for item in request.items:
                            upc_link = item['upc'].upc
                            kiosk_id = item['kiosk'].id
                            format_id = item['disk_format'].id
                            is_available = item['is_available']
                            if not request.db_session.query(ReservationCart).filter_by(upc_link=upc_link) \
                                    .filter_by(kiosk_id=kiosk_id).filter_by(disk_format_id=format_id) \
                                    .filter_by(user_id=user.id).filter_by(is_reserved=False).first():
                                res_cart = ReservationCart(upc_link, kiosk_id, format_id, user.id)
                                res_cart.is_available = is_available
                                request.db_session.add(res_cart)
                        request.db_session.commit()
                        response = json_response_content('success', "You've logged in successfully")
                    else:
                        response = json_response_content('success', "User is inactive")
                else:
                    response = json_response_content('error', "Wrong credentials or such user does not exist")
                    response['errors'] = auth_errors
            else:
                response = json_response_content('error', "Empty credentials")
                response['errors'] = auth_errors
        elif request.method == "GET":
            raise Http404
        else:
            raise Http404
    return JsonResponse(response)


@require_POST
def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return JsonResponse(json_response_content('success', "You've logged out successfully"))


@decorator_from_middleware(ReservationMiddleware)
def signup_step3(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            response = json_response_content()
            month = request.POST.get('cardExpiryMonth', '')
            year = request.POST.get('cardExpiryYear', '')
            card_number = request.POST.get('cardNumber', '')

            if month.isdigit() and int(month) in range(1, 13):
                len_month = len(month)
                if len_month < 3:
                    if len_month == 1:
                        month = '0' + month
                else:
                    response['type'] = 'error'
                    response['message'] = 'Please, enter valid month'
                    response['errors'].append(validation_error('cardExpiryMonth', 'Your month is invalid. Only 2 digits or less.'))
            else:
                response['type'] = 'error'
                response['message'] = 'Please, enter valid month'
                response['errors'].append(validation_error('cardExpiryMonth', 'Your month is invalid'))
            if year.isdigit() and ((int(year) in range(80, 100)) or (int(year) in range(0, int(str(date.today().year)[-2:])+1))):
                len_year = len(year)
                if len_year < 3:
                    if len_year == 1:
                        year = '0' + year
                else:
                    response['type'] = 'error'
                    response['message'] = 'Please, enter valid year'
                    response['errors'].append(validation_error('cardExpiryYear', 'Your year is invalid. Only 2 digits or less.'))
            else:
                response['type'] = 'error'
                response['message'] = 'Please, enter valid year'
                response['errors'].append(validation_error('cardExpiryYear', 'Your year is invalid'))

            card_expire = month + year

            if card_number and not response['message']:
                cc_number, cc_expiry = card_number, card_expire
                cc_number = str(cc_number)
                cc_number = str(int(cc_number) * 3)
                hash = hashlib.md5(cc_number + cc_expiry).hexdigest()
                card = request.db_session.query(Card).filter_by(hash=hash).filter_by(company_id=request.company.id).first()
                if card:
                    if card.user_id is None:
                        card.user_id = request.user.id
                        request.session['card_id'] = card.id
                    elif card.user_id != request.user.id:
                        return JsonResponse(json_response_content('error', 'This card does not belong to you'))
                else:
                    card = Card()
                    card.user_id = request.user.id
                    card.set_card(card_number, card_expire, '')
                    card.company_id = request.company.id
                    request.db_session.add(card)
                    request.session['card_id'] = card.id
                request.card = card
            else:
                response['type'] = 'error'
                response['message'] = 'No card number or expiration date'
                response['errors'].append(validation_error('cardNumber', 'No card number'))

            return JsonResponse(response)
        elif request.method == "GET":
            return render_to_response('site/registration/singup_step3.html', {},
            context_instance=RequestContext(request, processors=[sites_global]))
        else:
            raise Http404
    else:
        raise Http404


@decorator_from_middleware(ReservationMiddleware)
def signup_step2_default(request):
    return render_to_response('site/registration/singup_step2_default.html', {},
        context_instance=RequestContext(request, processors=[sites_global]))


@decorator_from_middleware(ReservationMiddleware)
def signup_step2_confirm(request, code):
    uce = request.db_session.query(UserConfirmationEmail) \
        .filter_by(confirmation_code=code) \
        .filter_by(dt_use=None) \
        .filter_by(company=request.company) \
        .first()
    if not uce:
        raise Http404

    if request.method == "POST":
        response = json_response_content()
        password1 = request.POST.get('new_password', '')
        password2 = request.POST.get('repeat_new_password', '')

        if not password1:
            response['type'] = 'error'
            response['message'] = 'Please, enter valid password'
            response['errors'].append(validation_error('new_password', 'Your password is invalid'))
        elif password1 != password2:
            response['type'] = 'error'
            response['message'] = "Your passwords don't match"
            response['errors'].append(validation_error('repeat_new_password', "Your passwords don't match"))
        else:
            uce.done(password1)
            request.db_session.commit()
            auth_errors = []
            user = auth.authenticate(username=uce.user.email,
                                     password=password1,
                                     user_type=[1],
                                     company_id=request.company.id,
                                     errors=auth_errors)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)

            if uce.no_errors() and not auth_errors:
                response['type'] = 'success'
                response['message'] = "Your password has been restored"
                response['redirect_url'] = reverse('sites.views.signup_step3')
            elif auth_errors:
                response['type'] = 'error'
                response['message'] = "Can not login"
                response['errors'] = uce.errors
            else:
                response['type'] = 'error'
                response['message'] = "Your password is invalid"
                response['errors'] = uce.errors
        return JsonResponse(response)
    elif request.method == "GET":
        return render_to_response('site/registration/signup_step2_save_new_pass.html', {},
            context_instance=RequestContext(request, processors=[sites_global]))
    else:
        raise Http404


@require_POST
@decorator_from_middleware(ReservationMiddleware)
def ajax_signup_step1(request):
    user = User()
    user.email = request.POST.get('email', u'').strip().lower()
    user.first_name = request.POST.get('firstName', u'')
    user.last_name = request.POST.get('lastName', u'')
    user.zip_code = request.POST.get('zipCode', u'')
    user.preferred_kiosk_id = request.POST.get('primaryKioskId', u'')
    user.company_id = request.company.id

    if user.preferred_kiosk_id not in [str(kiosk.id) for kiosk in request.company.active_kiosks]:
        user.errors.append({"field": "primaryKioskId", "message": "There is no such kiosk"})

    if request.db_session.query(User)\
            .filter_by(email=user.email)\
            .filter_by(user_type_id=1)\
            .filter(User.company == request.company).all():
        user.errors.append({"field": "email", "message": "Such email is already registered"})

    user.user_type_id = 1
    user.company_id = request.company.id
    if user.no_errors():
        request.db_session.add(user)
        uce = UserConfirmationEmail(user)
        text = """Press this link and follow commands to restore your password: \n %s
        If you can't follow the link, then just enter your code: %s
        to the following link: %s
        """ % ('http://%s%s' % (request.META['HTTP_HOST'],
                                reverse('sites.views.signup_step2_confirm',
                                        args=(uce.confirmation_code,),
                                        urlconf='sites.urls')),
               uce.confirmation_code,
               '%s/signup/step2/default' % request.META['HTTP_HOST'])
        mail.send_mail('Password restoring.',
                       text,
                       settings.DEFAULT_FROM_EMAIL,
                       [user.email],
                       fail_silently=False)
        request.db_session.add(uce)
        request.db_session.commit()
        response = json_response_content('success', "You've registered successfully")
        response['data'] = {
            'user': alchemy_to_json(user)
        }
    else:
        response = json_response_content('error', "Some error occurred during registration")
        for error in user.errors:
            response['errors'].append(error)
    return JsonResponse(response)


@require_GET
@decorator_from_middleware(ReservationMiddleware)
def signup_step1(request):
    return render_to_response('site/registration/signup_step1.html', {},
            context_instance=RequestContext(request, processors=[sites_global]))


def password_restore_confirm(request, code):
    urp = request.db_session.query(UserRestorePassword) \
        .filter_by(change_pass_code=code) \
        .filter_by(dt_use=None) \
        .filter_by(company=request.company) \
        .first()

    if not urp:
        raise Http404
        # return render(request, 'site/forgotpass/auth_404.html', {})

    if request.method == "POST":
        response = json_response_content()
        password1 = request.POST.get('new_password', '')
        password2 = request.POST.get('repeat_new_password', '')

        if not password1:
            response['type'] = 'error'
            response['message'] = 'Please, enter valid password'
            response['errors'].append(validation_error('new_password', 'Your password is invalid'))
        elif password1 != password2:
            response['type'] = 'error'
            response['message'] = "Your passwords don't match"
            response['errors'].append(validation_error('repeat_new_password', "Your passwords don't match"))
        else:
            urp.done(password1, field_name='new_password')
            if urp.no_errors():
                response['type'] = 'success'
                response['message'] = "Your password has been restored"
            else:
                response['type'] = 'error'
                response['message'] = "Your password is invalid"
                response['errors'] = urp.errors
        return JsonResponse(response)
    elif request.method == "GET":
        return render_to_response('site/forgotpass/resetpass.html', {},
            context_instance=RequestContext(request, processors=[sites_global]))
    else:
        raise Http404


def password_restore_default(request):
    return render_to_response('site/forgotpass/forgotpass.html', {},
        context_instance=RequestContext(request, processors=[sites_global]))


def password_restore(request):
    if request.user.is_authenticated():
        # FIXME: never used
        response = json_response_content('info', "You've already authenticated")
    else:
        if request.method == "POST":
            email = request.POST.get('email', '').strip().lower()
            try:
                validate_string_not_empty(email)
                validate_email(email)
                user = request.db_session.query(User)\
                    .filter_by(email=email)\
                    .filter(User.company == request.company)\
                    .filter(User.user_type_id == 1).first()
                if user is not None and user.is_active:
                    urp = UserRestorePassword(user)
                    text = """Press this link and follow commands to restore your password: \n %s
                    If you can't follow the link, then just enter your code: %s
                    to the following link: %s
                    """ % ('http://%s%s' % (request.META['HTTP_HOST'],
                                            reverse('sites.views.password_restore_confirm',
                                                    args=(urp.change_pass_code,),
                                                    urlconf='sites.urls')),
                           urp.change_pass_code,
                           '%s/password/restore/default' % request.META['HTTP_HOST'])
                    mail.send_mail('Password restoring.',
                                   text,
                                   settings.DEFAULT_FROM_EMAIL,
                                   [email],
                                   fail_silently=False)
                    request.db_session.add(urp)

                    response = json_response_content('success',
                        'Email with link to password restore was successfully sent you.')
                    request.db_session.commit()
                else:
                    # In case of fail, returning mistake
                    response = json_response_content('error', 'This email is not registered')
                    response['errors'].append({'field': 'email', 'message': 'This email is not registered'})
            except Exception, e:
                response = json_response_content('error', 'Your email is invalid')
                response['errors'].append(validation_error('email', unicode(e.message)))
    return JsonResponse(response)


def register_user(request):
    username = request.POST.get('email', u'')
    password = request.POST.get('password', u'')
    user = User(username, password)

    if request.db_session.query(User)\
            .filter_by(email=username)\
            .filter_by(user_type_id=1)\
            .filter(User.company == request.company).all():
        user.errors.append('email', 'Such email is already registered')

    user.user_type_id = 1
    user.company_id = request.company.id
    if user.no_errors():
        request.db_session.add(user)
        request.db_session.commit()
        response = json_response_content('success', "You've registered successfully")
        response['data'] = {
            'user': alchemy_to_json(user)
        }
    else:
        response = json_response_content('error', "Some error occurred during registration")
        for error in user.errors:
            response['errors'].append(error)
    return JsonResponse(response)


@decorator_from_middleware(ReservationMiddleware)
def cart(request):
    # Multiple tabs issue
    if request.preferred_kiosk:
        empty_slots = int(request.preferred_kiosk.settings.max_disks_per_card) - len(request.items)
        iterator = [None]*empty_slots if empty_slots > 0 else []
        if request.user.is_authenticated():
            items = map(lambda x: not x.is_available, request.items)
            disks_data = map(lambda x: (x.upc, x.kiosk, x.is_available, x.discount), request.items)
            reserved_in_cart = request.db_session.query(ReservationCart)\
                .filter_by(user_id=request.user.id).filter_by(is_reserved=True).all()
            for disk in reserved_in_cart:
                request.db_session.delete(disk)
        else:
            items = map(lambda x: not x['is_available'], request.items)
            print request.items
            disks_data = map(lambda x: (x['upc'], x['kiosk'], x['is_available'], x['discount']), 
                request.items)
        return render(request, 'site/reservation/cart.html', {
            'empty_slots': iterator,
            'not_available_items': any(items),
            'payments': expected_total_rent(disks_data),
            'valid_card': True
        })
    else:
        return HttpResponseRedirect(reverse('sites.views.index'))


@require_POST
@decorator_from_middleware(ReservationMiddleware)
def add_to_cart(request):
    movie_id = request.POST.get('movieId', None)
    format_id = request.POST.get('formatId', None)
    kiosk_id = request.POST.get('kioskId', None)
    if not request.preferred_kiosk and not kiosk_id:
        suitable_kiosks = kiosks_with_movie(request, movie_id, format_id)
        response = json_response_content('success', 'You have no preferred kiosk. Choose please')
        html = TemplateResponse(request, 'site/modals/kiosks_with_movies.html', 
            {'kiosks_with_movie': suitable_kiosks})
        html.render()
        response['data'] = {
            'template': html.content
        }
    else:
        response = json_response_content()
        if (request.preferred_kiosk and kiosk_id and kiosk_id != request.preferred_kiosk.id) or kiosk_id:
            change_preferred_kiosk(request, kiosk_id)
            html = TemplateResponse(request, 'site/partials/movie_info_list.html',
                {'movies': request.last_found_movies})
            html.render()
            response['data']['partial'] = html.content
        upc = None
        query = request.db_session.query(UpcMovie).join(UPC).join(Disk).join(Slot) \
            .filter(and_(Slot.kiosk_id == request.preferred_kiosk.id,
                         Disk.state_id == 0,
                         Slot.status_id == 1,
                         UpcMovie.movie_id == movie_id,
                         UpcMovie.disk_format_id == format_id))
        try:
            upc_movie = query.one()
            upc = upc_movie.upc
        except NoResultFound:
            response = json_response_content('info',
                                             'No such disk in chosen kiosk. Try others!')
            suitable_kiosks = kiosks_with_movie(request, movie_id, format_id)
            html = TemplateResponse(request, 'site/modals/kiosks_with_movies.html', 
                {'kiosks_with_movie': suitable_kiosks})
            html.render()
            response['data'] = {
                'partial': html.content
            }
        except MultipleResultsFound:
            upc = query.first().upc
        except Exception, e:
            response = json_response_content('error', 'Some errors occured')
            print e
        if upc:
            if format_id:
                response = json_response_content('success', 'Added to cart successfully')
                if request.user.is_authenticated():
                    disks_amount = request.db_session \
                        .query(ReservationCart) \
                        .filter_by(user_id=request.user.id) \
                        .filter_by(is_reserved=False).count()
                    empty_slots = int(request.preferred_kiosk.settings.max_disks_per_card) - disks_amount
                    if empty_slots > 0:
                        ucart = request.db_session.query(ReservationCart).filter_by(upc_link=upc)\
                            .filter_by(kiosk_id=request.preferred_kiosk.id)\
                            .filter_by(disk_format_id=format_id)\
                            .filter_by(user_id=request.user.id)
                        try:
                            user_cart = ucart.one()
                            user_cart.is_reserved = False
                        except Exception, e:
                            print e
                            for item in ucart.all():
                                request.db_session.delete(item)
                            user_cart = ReservationCart(upc, request.preferred_kiosk.id, 
                                format_id, request.user.id)
                            request.db_session.add(user_cart)
                            request.db_session.commit()
                    else:
                        return JsonResponse(json_response_content('warning', "Disk can't be added. Your cart is full."))
                else:
                    disks_amount = len(request.session['cart'])
                    empty_slots = int(request.preferred_kiosk.settings.max_disks_per_card) - disks_amount
                    if empty_slots > 0:
                        new_item = cart_item(upc, request.preferred_kiosk.id, format_id, 0)
                        if new_item not in request.session['cart']:
                            request.session['cart'].append(new_item)
                            request.session.modified = True
                    else:
                        return JsonResponse(json_response_content('warning', "Disk can't be added. Your cart is full."))

                response['data']['disks_amount'] = disks_amount + 1
                response['data']['name'] = request.preferred_kiosk.settings.alias
            else:
                response = json_response_content('error', 'Something went wrong')
                if not format_id:
                    response['errors'].append(validation_error('formatId', 'Choose disk format please'))
    return JsonResponse(response)


@decorator_from_middleware(ReservationMiddleware)
def preferred_kiosk(request):
    from urlparse import urlparse

    if request.method == "POST":
        kiosk_id = request.POST.get('kioskId', None)
        if kiosk_id:
            request.session['preferred_kiosk'] = int(kiosk_id) if kiosk_id is not None else kiosk_id
            change_cart_kiosk(request, kiosk_id)
            request.session.modified = True
            response = json_response_content('success', 'Your preferences were successfully saved')
            if urlparse(request.META['HTTP_REFERER']).path == '/cart/':
                empty_slots = int(request.preferred_kiosk.settings.max_disks_per_card - len(request.items))
                if request.user.is_authenticated():
                    items = map(lambda x: not x.is_available, request.items)
                    disks_data = map(lambda x: (x.upc, x.kiosk, x.is_available, x.discount), request.items)
                else:
                    items = map(lambda x: not x['is_available'], request.items)
                    disks_data = map(lambda x: (x['upc'], x['kiosk'], x['is_available'], x['discount']),
                        request.items)
                html = TemplateResponse(request, 'site/reservation/ajax_cart.html', 
                    {'empty_slots': [None]*empty_slots, 'not_available_items': any(items),
                        'payments': expected_total_rent(disks_data), 'valid_card': True})
                html.render()
                response['data'] = {
                    'cartTemplate': html.content
                }
        else:
            response = json_response_content('error', 'No id was supplied - no kiosk was chosen')
        return JsonResponse(response)
    else:
        raise Http404
        # return render(request, 'site/404.html', {})


@require_GET
@decorator_from_middleware(ReservationMiddleware)
def preferred_kiosk_movies(request):
    if request.preferred_kiosk:
        per_page = int(request.GET.get('perPage', 10))
        page = int(request.GET.get('page', 1))
        infinite = request.GET.get('inf', False)

        movies = filter_movies(request, and_(
            Slot.kiosk_id == request.preferred_kiosk.id,
            # Why in (0, 3)? 3 - means disk rented out.
            Disk.state_id.in_((0, 3)))
        )

        kiosk_genres = request.db_session.query(MovieGenreTranslation.value).distinct(MovieGenreTranslation.value) \
            .join(MovieMovieGenre, MovieGenreTranslation.movie_genre_id == MovieMovieGenre.movie_genre_id) \
            .join(UpcMovie, MovieMovieGenre.movie_id == UpcMovie.movie_id) \
            .join(Disk, UpcMovie.upc == Disk.upc_link) \
            .join(Slot, Disk.slot_id == Slot.id) \
            .filter(and_(Slot.kiosk_id == request.preferred_kiosk.id,
                         Slot.status_id == 1
                         )).filter(MovieGenreTranslation.language_id == 1).all()
        kiosk_genres = map(itemgetter(0), kiosk_genres)

        # p = Paginator(request.get_full_path(), movies.count(), per_page)
        # try:
        #     cur_page = p.page(page)
        # except:
        #     return render(request, 'site/404.html', {})

        if infinite:
            return render_to_response('site/partials/movie_info_list.html', {
                'movies': movies.offset(per_page * (page - 1)).limit(per_page),
                'page': page
            }, context_instance=RequestContext(request, processors=[sites_global]))
        else:
            return render_to_response('site/movies/movies.html', { 
                'movies': movies.offset(per_page * (page - 1)).limit(per_page),
                'kiosk_genres': kiosk_genres,
                'kiosk': request.preferred_kiosk,
                'multiple_pages': movies.count() > per_page
            }, context_instance=RequestContext(request, processors=[sites_global]))
    else:
        return HttpResponseRedirect(reverse('sites.views.index'))


@decorator_from_middleware(ReservationMiddleware)
def check_cart(request):
    if request.user.is_authenticated():
        items = request.db_session.query(ReservationCart.is_available).filter_by(user_id=request.user.id)\
            .filter_by(is_reserved=False).all()
        items = map(lambda x: not x[0], items)
        if any(items):
            response = json_response_content('error', 'Not all disks are present in this kiosk')
        else:
            response = json_response_content('success', 'Everything is good. Please, choose card')

    else:
        response = json_response_content('warning', 'You are not authorized. Please authorize')
    return JsonResponse(response)


@require_POST
@decorator_from_middleware(ReservationMiddleware)
def choose_card(request):
    if request.user.is_authenticated():
        card_id = request.POST.get('cardId', None)
        card_number = request.POST.get('cardNumber', None)
        card_expire = request.POST.get('cardExpiry', None)

        if card_number and card_expire:
            kiosk = request.db_session.query(Kiosk).filter(Kiosk.id == request.session['preferred_kiosk']).first()

            card = request.db_session.query(Card)\
                .filter(Card.company == kiosk.company)\
                .filter_by(hash=Card.get_hash({'cc_expiry': card_expire,
                                               'cc_number': card_number})).first()
            if card:
                if card.user_id is None:
                    card.user_id = request.user.id
                    request.session['card_id'] = card.id
                    request.card = card
                elif card.user_id != request.user.id:
                    return JsonResponse(json_response_content('error', 'This card does not belong to you'))
            else:
                message = 'This card wasn\'t used by current user with this kiosk\'s company. Please, use directly kiosk at first'
                response = json_response_content('error', message)
                response['errors'].append({'field': 'cardNumber', 'message': message})
                return JsonResponse(response)
        elif card_id:
            request.session['card_id'] = card_id
            request.card = request.db_session.query(Card).filter_by(id=card_id).first()
        else:
            return JsonResponse(json_response_content('error', 'No card number or expiration date'))
            
        response = approve_reservations(request)
        request.session.modified = True
    else:
        response = json_response_content('warning', 'You are not authorized. Please authorize')
    return JsonResponse(response)


@require_POST
@decorator_from_middleware(ReservationMiddleware)
def remove_from_cart(request):
    """
    Removes disk from reservation card by kiosk_id, upc, format_id.
    If user is authenticated, it uses database ReservationCart table,
    else it removes records from request.session
    """
    format_id = request.POST.get('formatId', None)
    kiosk_id = request.POST.get('kioskId', None)
    upc = request.POST.get('upc', None)
    if request.user.is_authenticated():
        rc = request.db_session.query(ReservationCart)\
            .filter_by(user=request.user) \
            .filter_by(kiosk_id=kiosk_id)\
            .filter_by(upc_link=upc)\
            .filter_by(disk_format_id=format_id).first()
        request.db_session.delete(rc)
        request.db_session.commit()
        # just stub
        request.items = request.db_session.query(ReservationCart)\
            .filter_by(user_id=request.user.id) \
            .filter_by(is_reserved=False).all()
        if request.items and request.items[0].coupon:
            cp = CouponProcessor(request.items[0].coupon)
            cp.expected_discount(request.items)
    else:
        # NOTE in middleware about it!
        # think of refactoring
        # rc = [i for i in request.items
        #       if i['upc'].upc == upc and
        #       str(i['kiosk'].id) == kiosk_id and
        #       str(i['disk_format'].id) == format_id]
        # if rc:
        #     request.items.remove(rc[0])
        rc = [i for i in request.session['cart']
              if i[u'format_id'] == format_id and
              i[u'kiosk_id'] == int(kiosk_id) and
              i[u'upc'] == upc]
        if rc:
            request.session['cart'].remove(rc[0])
            request.session.modified = True
            # just stub
            rc = [i for i in request.items
                  if i['upc'].upc == upc and
                  str(i['kiosk'].id) == kiosk_id and
                  str(i['disk_format'].id) == format_id]
            if rc:
                request.items.remove(rc[0])

    response = json_response_content('success',
                                     'Your item was successfully deleted')
    empty_slots = int(request.preferred_kiosk.settings.max_disks_per_card - len(request.items))
    if request.user.is_authenticated():
        items = map(lambda x: not x.is_available, request.items)
        disks_data = map(lambda x: (x.upc, x.kiosk, x.is_available, x.discount), request.items)
    else:
        items = map(lambda x: not x['is_available'], request.items)
        disks_data = map(lambda x: (x['upc'], x['kiosk'], x['is_available'], x['discount']), 
            request.items)
    html = TemplateResponse(request, 'site/reservation/ajax_cart.html',
        {'empty_slots': [None]*empty_slots, 'not_available_items': any(items),
            'payments': expected_total_rent(disks_data), 'valid_card': True})
    html.render()
    response['data'] = {
        'cartTemplate': html.content,
        'disks_amount': len(request.items)
    }
    return JsonResponse(response)


@require_GET
@decorator_from_middleware(ReservationMiddleware)
def user_reservations(request):
    if request.user.is_authenticated():
        reservations = request.db_session.query(Deal).join(Card) \
            .filter(Deal.deal_status_id == 241) \
            .filter(Card.user_id == request.user.id) \
            .all()
        return render_to_response('site/reservation/reserved.html', {'reservations': reservations},
                                  context_instance=RequestContext(request, processors=[sites_global]))
    else:
        # return render(request, 'site/404.html', {})
        raise Http404


@require_GET
@decorator_from_middleware(ReservationMiddleware)
def user_reservation(request):
    secret_code = request.GET.get('code', None)
    if request.user.is_authenticated() and secret_code:
        thanks = request.GET.get('thanks', None)
        reservations = request.db_session.query(Deal) \
            .filter_by(deal_status_id=241) \
            .filter_by(secret_code=secret_code).all()
        return render_to_response('site/reservation/onereserved.html',
                                  {'reservations': reservations, 'thanks': thanks},
                                  context_instance=RequestContext(request, processors=[sites_global]))
    else:
        # return render(request, 'site/404.html', {})
        raise Http404


@require_POST
@decorator_from_middleware(ReservationMiddleware)
def add_coupon(request):
    coupon_code = request.POST.get('couponCode', None)
    coupon = request.db_session.query(Coupon)\
        .filter_by(company_id=request.company.id) \
        .filter_by(code=coupon_code)\
        .filter(Coupon.is_deleted.isnot(True)).first()
    if coupon:
        if coupon.is_active:
            cp = CouponProcessor(coupon)
            cp.expected_discount(request.items)
            if request.user.is_authenticated():
                for item in request.items:
                    item.coupon = coupon
                request.db_session.add_all(request.items)
                request.db_session.commit()
                items = map(lambda x: not x.is_available, request.items)
                disks_data = map(lambda x: (x.upc, x.kiosk, x.is_available, x.discount), request.items)
            else:
                items = map(lambda x: not x['is_available'], request.items)
                disks_data = map(lambda x: (x['upc'], x['kiosk'], x['is_available'], x['discount']), request.items)
            response = json_response_content('success', 'Coupon was successfully added')
            empty_slots = int(request.preferred_kiosk.settings.max_disks_per_card - len(request.items))
            html = TemplateResponse(request, 'site/reservation/ajax_cart.html',
                {'empty_slots': [None]*empty_slots, 'not_available_items': any(items),
                    'payments': expected_total_rent(disks_data), 'valid_card': True})
            html.render()
            response['data'] = {
                'cartTemplate': html.content,
                'disks_amount': len(request.items)
            }
        else:
            response = json_response_content('error', 'This coupon has expired')
            response['errors'].append(validation_error('couponCode', 
                'This coupon has not started yet or already expired'))
    else:
        response = json_response_content('error', 'Wrong coupon code is given')
        response['errors'].append(validation_error('couponCode', 'Wrong coupon code is given'))
    return JsonResponse(response)


@decorator_from_middleware(ReservationMiddleware)
def personal_data(request):
    user_is_authenticated(request)
    return render_to_response('site/personal_data/personal_data.html', {},
        context_instance=RequestContext(request, processors=[sites_global]))


@require_POST
@decorator_from_middleware(ReservationMiddleware)
def ajax_personal_data(request):
    user_is_authenticated(request)
    user = request.db_session.query(User).filter_by(id=request.user.id).first()
    user.email = request.POST.get('email', u'').strip().lower()
    user.first_name = request.POST.get('firstName', u'')
    user.last_name = request.POST.get('lastName', u'')
    user.zip_code = request.POST.get('zipCode', u'')
    user.preferred_kiosk_id = request.POST.get('primaryKioskId', u'')
    user.company_id = request.company.id

    if user.preferred_kiosk_id not in [str(kiosk.id) for kiosk in request.company.active_kiosks]:
        user.errors.append({"field": "primaryKioskId", "message": "There is no such kiosk"})

    user.user_type_id = 1
    user.company_id = request.company.id
    if user.no_errors():
        request.db_session.add(user)
        request.db_session.commit()
        response = json_response_content('success', "You've registered successfully")
        response['data'] = {
            'user': alchemy_to_json(user)
        }
    else:
        request.db_session.rollback()
        response = json_response_content('error', "Some error occurred during registration")
        for error in user.errors:
            response['errors'].append(error)
    return JsonResponse(response)


@decorator_from_middleware(ReservationMiddleware)
def change_password(request):
    user_is_authenticated(request)
    return render_to_response('site/change_password/change_password.html', {},
        context_instance=RequestContext(request, processors=[sites_global]))


@decorator_from_middleware(ReservationMiddleware)
def ajax_change_password(request):
    user_is_authenticated(request)
    user = request.db_session.query(User).filter_by(id=request.user.id).first()
    old_pass = request.POST.get('old_password', u'')
    new_pass = request.POST.get('password', u'')
    rep_pass = request.POST.get('repeat_password', u'')

    if not request.user.is_pass_valid(old_pass):
        user.errors.append({"field": "old_password", "message": "Wrong old password"})
    elif len(new_pass) <= 4:
        user.errors.append({"field": "password", "message": "Too short password"})
    elif new_pass != rep_pass:
        user.errors.append({"field": "repeat_password", "message": "Passwords doesn't match"})
    else:
        request.user.set_password(new_pass, field_name='password')
        if user.no_errors():
            response = json_response_content('success', "You've registered successfully")
            return JsonResponse(response)
    response = json_response_content('error', "Some error occurred while changing password")
    response['errors'] = user.errors
    return JsonResponse(response)


@decorator_from_middleware(ReservationMiddleware)
def credit_cards(request):
    user_is_authenticated(request)
    cards = request.db_session.query(Card).filter_by(user_id=request.user.id, is_active=True).order_by("dt_add desc").all()
    return render_to_response('site/credit_cards/credit_cards.html', {'cards': cards},
        context_instance=RequestContext(request, processors=[sites_global]))


@decorator_from_middleware(ReservationMiddleware)
def add_credit_card(request):
    user_is_authenticated(request)
    return render_to_response('site/credit_cards/add_credit_card.html', {},
        context_instance=RequestContext(request, processors=[sites_global]))


@decorator_from_middleware(ReservationMiddleware)
def ajax_add_credit_card(request):
    user_is_authenticated(request)
    user = request.db_session.query(User).filter_by(id=request.user.id).first()
    card = Card()
    card.errors = []
    card_number = request.POST.get('cardNumber', u'')
    card_holder = request.POST.get('cardHolder', u'')
    card_expiry_month = request.POST.get('cardExpiryMonth', u'')
    card_expiry_year = request.POST.get('cardExpiryYear', u'')

    if not card_number:
        card.errors.append({"field": "cardNumber", "message": "Empty field"})
    elif not card_number.isdigit():
        card.errors.append({"field": "cardNumber", "message": "Need only digits"})
    elif not (len(card_number) == 16):
        card.errors.append({"field": "cardNumber", "message": "Need 16 numbers long"})

    if not card_holder:
        card.errors.append({"field": "cardHolder", "message": "Empty field"})
    elif not re.match("^[A-Za-z0-9_-]*$", ''.join(card_holder.split())):
        card.errors.append({"field": "cardHolder", "message": "Need only latin symbols"})
    elif not (len(card_holder) <= 40):
        card.errors.append({"field": "cardHolder", "message": "Need less 40 symbols long"})

    valid_month, valid_year = False, False
    if not card_expiry_month:
        card.errors.append({"field": "cardExpiryMonth", "message": "Empty field"})
    elif not re.match("^[0-9]*$", card_expiry_month):
        card.errors.append({"field": "cardExpiryMonth", "message": "Need only digits"})
    elif not (int(card_expiry_month) in range(1, 13)):
        card.errors.append({"field": "cardExpiryMonth", "message": "In the interval from 1 to 12"})
    else:
        valid_month = True

    if not card_expiry_year:
        card.errors.append({"field": "cardExpiryYear", "message": "Empty field"})
    elif not re.match("^[0-9]*$", card_expiry_year):
        card.errors.append({"field": "cardExpiryYear", "message": "Need only digits"})
    elif not (len(card_expiry_year) <= 2):
        card.errors.append({"field": "cardExpiryYear", "message": "Need only 2 digits"})
    else:
        valid_year = True

    if valid_month and valid_year:
        now = int(datetime.utcnow().strftime('%y%m'))
        int_year, int_month = int(card_expiry_year), int(card_expiry_month)
        set = int('{0:02d}{1:02d}'.format(int_year, int_month))
        if not set >= now:
            card.errors.append({"field": "cardExpiryYear", "message": "The card has expired maintenance"})

        cc_number = card_number
        cc_expiry = '{0:02d}{1:02d}'.format(int_month, int_year)
        cardholder_name = ' '.join(card_holder.split())
        card.set_card(cc_number, cc_expiry, cardholder_name)
        card.company_id = request.company.id
        card.user = user
        card_find_other = request.db_session.query(Card)\
            .filter_by(hash=card.hash)\
            .filter_by(company=request.company)\
            .filter(Card.user != user)\
            .first()
        card_find_your = request.db_session.query(Card)\
            .filter_by(hash=card.hash)\
            .filter_by(company=request.company)\
            .filter_by(user = user)\
            .filter_by(is_active = True)\
            .first()
        if card_find_other or card_find_your:
            card.errors.append({"field": "cardNumber", "message": "Such card already exists"})

    if card.errors:
        response = json_response_content('error', "Some error occurred during add card")
        for error in card.errors:
            response['errors'].append(error)
        return JsonResponse(response)
    else:
        request.db_session.add(card)
        request.db_session.commit()
        response = json_response_content('success', 'Credit card was successfully added')
        response['data'] = {
            'card_name': card.value_to_display,
            'card_dt_add': card.dt_add.strftime('%m/%d/%y %H:%M:%S'),
            'url': reverse('sites.views.remove_credit_card', args=(card.id,))
        }
        return JsonResponse(response)


@require_GET
@decorator_from_middleware(ReservationMiddleware)
def remove_credit_card(request, credit_card_id):
    user_is_authenticated(request)
    user = request.db_session.query(User).filter_by(id=request.user.id).first()
    response = json_response_content('error', "Some error occurred during remove card")
    if credit_card_id:
        card = request.db_session.query(Card)\
            .filter_by(id=credit_card_id)\
            .filter_by(company=request.company)\
            .filter_by(user = user)\
            .filter_by(is_active = True)\
            .first()
        if card:
            card.is_active = False
            request.db_session.add(card)
            response = json_response_content('success', "You've removed card successfully")
    return JsonResponse(response)


@decorator_from_middleware(ReservationMiddleware)
def signup(request):
    redirect = page_for_logout_user(request)
    if redirect:
        return redirect
    return render_to_response('site/registration/signup.html', {},
        context_instance=RequestContext(request, processors=[sites_global]))


@require_POST
@decorator_from_middleware(ReservationMiddleware)
def ajax_signup_confirm(request):
    email = request.POST.get('email', u'').strip().lower()
    if email:
        user = request.db_session.query(User)\
                    .filter_by(email=email)\
                    .filter_by(user_type_id=1)\
                    .filter_by(company=request.company).first()
        request.db_session.add(user)
        uce = UserConfirmationEmail(user)
        text = """Press this link and follow commands to confirm your registration: \n %s
        If you can't follow the link, then just enter your code: %s
        to the following link: %s
        """ % ('http://%s%s' % (request.META['HTTP_HOST'],
                                reverse('sites.views.signup_confirm',
                                        args=(uce.confirmation_code,),
                                        urlconf='sites.urls')),
               uce.confirmation_code,
               '%s/signup/default' % request.META['HTTP_HOST'])
        mail.send_mail('Password restoring.',
                       text,
                       settings.DEFAULT_FROM_EMAIL,
                       [user.email],
                       fail_silently=False)
        request.db_session.add(uce)
        request.db_session.commit()
        response = json_response_content('success', "We send mail successfully")
        return JsonResponse(response)

@require_POST
@decorator_from_middleware(ReservationMiddleware)
def ajax_signup(request):
    user = User()
    user.email = request.POST.get('email', u'').strip().lower()
    user.first_name = request.POST.get('firstName', u'')
    user.last_name = request.POST.get('lastName', u'')
    user.zip_code = request.POST.get('zipCode', u'')
    user.set_password(request.POST.get('password', ''))
    user.preferred_kiosk_id = request.POST.get('primaryKioskId', u'')
    user.company_id = request.company.id

    if user.preferred_kiosk_id not in [str(kiosk.id) for kiosk in request.company.active_kiosks]:
        user.errors.append({"field": "primaryKioskId", "message": "There is no such kiosk"})

    password1 = request.POST.get('password', '')
    password2 = request.POST.get('repeat_password', '')
    if password1 and (password1 != password2):
        user.errors.append({"field": "repeat_password", "message": "Your passwords don't match"})

    user_temp = request.db_session.query(User)\
                    .filter_by(email=user.email)\
                    .filter_by(user_type_id=1)\
                    .filter_by(company=request.company).first()
    if user_temp:
        if not user_temp.is_email_valid:
            response = json_response_content('info', "Send email again")
            response['data'] = {'send_email_again': user.email}
            return JsonResponse(response)
        else:
            user.errors.append({"field": "email", "message": "Such email is already registered"})

    user.user_type_id = 1
    user.company_id = request.company.id
    if user.no_errors():
        request.db_session.add(user)
        uce = UserConfirmationEmail(user)
        text = """Press this link and follow commands to confirm your registration: \n %s
        If you can't follow the link, then just enter your code: %s
        to the following link: %s
        """ % ('http://%s%s' % (request.META['HTTP_HOST'],
                                reverse('sites.views.signup_confirm',
                                        args=(uce.confirmation_code,),
                                        urlconf='sites.urls')),
               uce.confirmation_code,
               '%s/signup/default' % request.META['HTTP_HOST'])
        mail.send_mail('Password restoring.',
                       text,
                       'noreply@focusintense.com',
                       [user.email],
                       fail_silently=False)
        request.db_session.add(uce)
        request.db_session.commit()
        response = json_response_content('success', "You've registered successfully")
        response['data'] = {
            'user': alchemy_to_json(user)
        }
    else:
        response = json_response_content('error', "Some error occurred during registration")
        for error in user.errors:
            response['errors'].append(error)
    return JsonResponse(response)


@decorator_from_middleware(ReservationMiddleware)
def signup_default(request):
    redirect = page_for_logout_user(request)
    if redirect:
        return redirect
    return render_to_response('site/registration/singup_default.html', {},
        context_instance=RequestContext(request, processors=[sites_global]))


@decorator_from_middleware(ReservationMiddleware)
def signup_confirm(request, code):
    redirect = page_for_logout_user(request)
    if redirect:
        return redirect
    uce = request.db_session.query(UserConfirmationEmail) \
        .filter_by(confirmation_code=code) \
        .filter_by(company=request.company) \
        .first()
    if not uce:
        str_error = "Confirmation link is not valid"
        if request.method == "POST":
            response = json_response_content('error', str_error)
            response['errors'].append({'field': 'code', 'message': str_error})
            return JsonResponse(response)
        return render_to_response('site/registration/404.html', {"error": str_error},
            context_instance=RequestContext(request, processors=[sites_global]))

    if uce.dt_use:
        str_error = "Registraion has been already confirmed"
        if request.method == "POST":
            response = json_response_content('error', str_error)
            response['errors'].append({'field': 'code', 'message': str_error})
            return JsonResponse(response)
        return render_to_response('site/registration/404.html', {"error": str_error},
            context_instance=RequestContext(request, processors=[sites_global]))
    else:
        uce.dt_use = datetime.utcnow()
        uce.user.backend = 'authentication.backends.EmailBackend'
        uce.user.is_email_valid = True
        auth.login(request, uce.user)
        request.db_session.commit()
    if request.method == "POST":
        response = json_response_content('success', "You are confirm successfully")
        response['redirect_url'] = reverse('sites.views.personal_data')
        return JsonResponse(response)
    return HttpResponseRedirect(reverse('sites.views.personal_data'))

