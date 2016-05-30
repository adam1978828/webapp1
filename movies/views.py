import hashlib
import uuid
import datetime
import os

from django.shortcuts import render
from django.http import JsonResponse, Http404, StreamingHttpResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import condition, require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.conf import settings

from sqlalchemy import or_
from json import loads

from Model import MovieRating, Movie, MovieGenre, MovieTranslation, \
    MovieGenreTranslation, MovieMovieGenre, UpdateMoviesStatsAlt, \
    Language, DiskFormat, UPC, UpcMovie, FeaturedMovie, Disk, Slot, MoviesView
from WebApp.utils import save_file, alchemy_to_json
from libs.validators.core import json_response_content

from datatables import ColumnDT, DataTables
from acc.decorators import permission_required

__author__ = "D.Kalpakchi"


# Create your views here.
@login_required
def all(request):
    return render(request, 'movies_all.html', {})


def _unknown_column_value(val):
    return val if val is not None else '-'


def _date_column(val):
    return val.strftime('%m/%d/%y') if val is not None else '-'


def _unrated_movie(val):
    return val if val is not None else 'NR'


def _edit_movie_button(val):
    controls = '<a class="button small grey tooltip" data-gravity="s" href="{0}"><i class="icon-pencil"></i></a>'.\
        format(reverse('movies.views.add_edit', args=('edit', val,)))
    return controls


@login_required
def json_all(request):
    columns = list()
    columns.append(ColumnDT('id'))
    columns.append(ColumnDT('upc', filter=_unknown_column_value))
    columns.append(ColumnDT('title', filter=_unknown_column_value))
    columns.append(ColumnDT('length', filter=_unknown_column_value))
    columns.append(ColumnDT('dt_release', filter=_date_column))
    columns.append(ColumnDT('dt_dvd_release', filter=_date_column))
    columns.append(ColumnDT('rating', filter=_unrated_movie))
    columns.append(ColumnDT('dt_modify', filter=_date_time_column))
    columns.append(ColumnDT('id', filter=_edit_movie_button))

    query = request.db_session.query(MoviesView)
    row_table = DataTables(request, MoviesView, query, columns)
    response = row_table.output_result()
    return JsonResponse(response)


@login_required
def ajax_load_all(request):
    movies = request.db_session.query(Movie, MovieTranslation).outerjoin(MovieTranslation)\
        .filter(or_(MovieTranslation.language_id == 1, MovieTranslation.language_id == None))
    data = { 'aaData': [] }
    data['aaData'] = [[m.id, 
        m_t.name if m_t else '!!NONE!!',
        int(m.length) if m.length else 'UNK',
        int(m.release_year) if m.release_year else 'UNK',
        m.movie_rating.value if m.movie_rating else 'NR',
        m.dt_modify.strftime('%x %X')
    ] for m, m_t in movies]
    return JsonResponse(data)


@login_required
@permission_required('movies_add')
def add_edit(request, mode, movie_id=None):
    if request.method == "GET":

        if mode == 'edit':
            movie = request.db_session.query(Movie).filter(Movie.id == movie_id).first()
            if not movie:
                raise Http404

            movie_trans = request.db_session.query(MovieTranslation).filter(MovieTranslation.movie_id == movie_id).all()
            exclude_langs = [val.language_id for val in movie_trans]
        else:
            movie = None
            movie_trans = None
            exclude_langs = []

        ratings = request.db_session.query(MovieRating).all()
        languages = request.db_session.query(Language).all()
        return render(request, 'movies_add_edit.html', {'ratings': ratings, 'languages': languages,
                                                        'mode': mode, 'movie': movie,
                                                        'movie_trans': movie_trans, 'exclude_langs': exclude_langs})
    elif request.method == "POST":
        cover = request.FILES.get('cover', None)
        movie_info = loads(request.POST.get('movie', None))

        if movie_info:
            length = movie_info.get('length', None)
            release_year = movie_info.get('releaseYear', None)

            release_date = movie_info.get('releaseDate', None)
            release_date = datetime.datetime.strptime(release_date, '%m/%d/%Y') if release_date else None

            release_dvd_date = movie_info.get('dvdReleaseDate', None)
            release_dvd_date = datetime.datetime.strptime(release_dvd_date, '%m/%d/%Y') if release_dvd_date else None

            rating_id = movie_info['rating']
            translations = movie_info.get('translations', None)

            if mode == 'add':
                movie = Movie(length=length, release_year=release_year, dt_release=release_date, dt_dvd_release=release_dvd_date)
            else:
                movie = request.db_session.query(Movie).filter(Movie.id == movie_id).first()
                movie.dt_dvd_release = release_dvd_date
                movie.dt_release = release_date
                movie.release_year = release_year
                movie.length = length

            if rating_id:
                movie.movie_rating_id = rating_id
            if translations:
                if mode == 'edit':
                    request.db_session.query(MovieTranslation).filter(MovieTranslation.movie_id == movie_id).delete()

                for translation in translations:
                    title = translation['title']
                    desc = translation['description']

                    lang = request.db_session.query(Language).filter_by(id=int(translation['id'])).first()
                    t = MovieTranslation(title, desc, lang, movie)

                    if t.no_errors():
                        request.db_session.add(t)
                    else:
                        response = json_response_content('error', _('Some error occurred on movie {0}!'.format(_('added') if mode == 'add' else _('saved'))))
                        for error in t.errors:
                            response['errors'].append(error)
            else:
                response = json_response_content('error', 'At least one translation must be specified!')
                return JsonResponse(response)

            if cover:
                extension = os.path.splitext(cover.name)[-1].lstrip('.')
                img_path = '/%s.%s' % (uuid.uuid4().hex, extension)
                path = os.path.join(settings.POSTER_DIR, img_path.strip('/'))
                save_file(cover, path)
                movie.img_path = img_path
                movie_file = open(path)
                movie_hash = hashlib.md5(movie_file.read()).hexdigest()

            if movie.no_errors():
                movie.is_manual_edit = True
                request.db_session.add(movie)
                request.db_session.commit()
                response = json_response_content('success', _('Movie was successfully {0}!').format(_('added') if mode == 'add' else _('saved')))

                response['redirect_url'] = reverse('movies.views.add_edit', args=('edit', movie.id)) if mode == 'add' else ''
            else:
                if not 'response' in locals():
                    response = json_response_content('error', _('Some error occurred on movie {0}!'.format(_('add') if mode == 'add' else _('save'))))
                for error in movie.errors:
                    response['errors'].append(error)
        else:
            response = json_response_content('error', 'No info about movie given')
        return JsonResponse(response)
    else:
        raise Http404


@login_required
@permission_required('movie_add_upc')
def add_upc(request):
    if request.method == "GET":
        movies = request.db_session.query(Movie).limit(10)
        formats = request.db_session.query(DiskFormat).all()
        return render(request, 'movies_add_upc.html', {'movies': movies, 'formats': formats})
    elif request.method == "POST":
        upcLink = request.POST.get('upc', None)
        movie_id = request.POST.get('movieId', None)
        format_id = request.POST.get('diskFormatId', None)
        if request.db_session.query(UPC).filter_by(upc=upcLink).count():
            response = json_response_content('warning', 'UPC %s already exists' % upcLink)
        else:
            upc = UPC(upc=upcLink)
            upc_movie = UpcMovie(upcLink, movie_id, format_id)
            if upc.no_errors() and upc_movie.no_errors():
                request.db_session.add_all([upc, upc_movie])
                request.db_session.commit()
                response = json_response_content('success', 'UPC was added successfully')
            else:
                response = json_response_content('error', 'Some errors occured during creating UPC')
                for error in upc.errors:
                    response['errors'].append(error)
                for error in upc_movie.errors:
                    response['errors'].append(error)
        return JsonResponse(response)
    else:
        raise Http404


@login_required
@permission_required('movies_edit_featured')
def search(request):
    '''
    Movie live search
    '''
    if request.method == 'GET':
        resPerTime = request.GET.get('resPerTime', 7)
        name_part = request.GET.get('movie', '')
        movie_result = request.db_session.query(MovieTranslation.movie_id, MovieTranslation.name)\
            .filter(MovieTranslation.name.ilike('%{0}%'.format(name_part)))
        return JsonResponse({
            'query': name_part,
            'movies': movie_result.limit(resPerTime).all() if resPerTime > 0 else movie_result.all(),
            'movies_amount': movie_result.count() - resPerTime
        })
    else:
        raise Http404


@require_GET
def search_by_title(request):
    name_part = request.GET.get('movie', '')
    kiosk_id = request.GET.get('kioskId', None)
    movies = request.db_session.query(Movie).join(MovieTranslation)\
        .join(UpcMovie).join(UPC).join(Disk).join(Slot)\
        .filter(MovieTranslation.name.ilike('%{0}%'.format(name_part)))
    if kiosk_id:
        movies = movies.filter(Slot.kiosk_id == kiosk_id)
    result = []
    for movie in movies.all():
        for format in movie.disk_formats:
            for upc in movie.upc_matching(format.id):
                result.append([movie.get_name, movie.release_year, format.name, upc]) 
    return JsonResponse({
        'results': result
    })


@login_required
@permission_required('movies_update')
def update_center_alt(request, type_alias):
    if request.method == 'POST':
        if type_alias == 'full_load':
            from rabbit_mq.rabbit import rbbt_load_movie_data
            rbbt_load_movie_data.delay(request.user.id, True)

            # from updater import load_movie_data
            # load_movie_data(request.user.id, True)

            return JsonResponse(json_response_content('success', "Movie update started!"))
        elif type_alias == 'hash_update':
            from rabbit_mq.rabbit import rbbt_update_movie_poster_hash
            rbbt_update_movie_poster_hash.delay(request.user.id, True)

            # from updater import update_image_hash
            # update_image_hash(request.user.id, True)

            return JsonResponse(json_response_content('success', "Posters file hash update started!"))
        else:
            return JsonResponse(json_response_content('error', "Invalid update type in JSON!"))
    else:
        last_update_stats = request.db_session \
            .query(UpdateMoviesStatsAlt) \
            .order_by(UpdateMoviesStatsAlt.id.desc()).first()
        context = {'last_update_stats': last_update_stats}
        return render(request, 'movies_update_center_alt.html', context)


def _date_time_column(val):
    return val.strftime('%m/%d/%y %I:%M %p') if val is not None else '-'


def _run_by(val):
    return _('System') if val is None else val.full_name


def _status_name(val):
    return val.name


def _update_type_name(val):
    return val.name if val else 'null'


@login_required
@permission_required('movies_update')
def refresh_update_center(request):
    last_update_stats = request.db_session.query(UpdateMoviesStatsAlt).order_by(UpdateMoviesStatsAlt.id.desc()).first()
    data = {
        'finalized': last_update_stats.dt_end is not None,
        'start_dt': _date_time_column(last_update_stats.dt_start),
        'status': last_update_stats.status.name,
        'detected': int(last_update_stats.detected),
        'exists': int(last_update_stats.existed),
        'not_recognized': int(last_update_stats.not_recognized),
        'saved': int(last_update_stats.stored),
        'hash_handled': int(last_update_stats.hash_handled)
    }
    return JsonResponse(data)


@login_required
def json_update_center_log(request):
    columns = list()

    columns.append(ColumnDT('id'))
    columns.append(ColumnDT('update_type', filter=_update_type_name))
    columns.append(ColumnDT('dt_start', filter=_date_time_column))
    columns.append(ColumnDT('dt_end', filter=_date_time_column))
    columns.append(ColumnDT('dt_modify', filter=_date_time_column))
    columns.append(ColumnDT('user', filter=_run_by))
    columns.append(ColumnDT('_status', filter=_status_name))

    query = request.db_session.query(UpdateMoviesStatsAlt)
    row_table = DataTables(request, UpdateMoviesStatsAlt, query, columns)
    response = row_table.output_result()

    return JsonResponse(response)


@login_required
def update_images(request):
    from parse_csv import update_movies_images
    return StreamingHttpResponse(update_movies_images())

###############################
#
# Featured movies views
#
###############################


@login_required
@permission_required('movies_view_featured')
def featured(request):
    if request.method == "POST":
        if 'movies_edit_featured' not in request.user.rights:
            raise PermissionDenied
        try:
            movie_id = int(request.POST.get('movieId'))
        except Exception, e:
            print e 
            return JsonResponse(json_response_content('error',
                                                      'No movie was given.'))
        try:
            movie = request.db_session.query(Movie).filter_by(id=movie_id).first()
            company_id = request.user.company.id
            featured = FeaturedMovie(company_id, movie_id)
            request.db_session.merge(featured)
            response = json_response_content('success',
                                             'Movie was featured successfully')
            response['data'] = {
                'movieId': movie_id,
                'id': request.db_session.query(FeaturedMovie).count(),
                'name': movie.get_name,
                'length': movie.length,
                'release':  _date_column(movie.dt_release),
                'releaseDvd': _date_column(movie.dt_dvd_release),
                'isActive': featured.is_active,
                'dtModify': _date_time_column(featured.dt_modify)
            }
            request.db_session.commit()
            return JsonResponse(response)
        except Exception, e:
            request.db_session.rollback()
    elif request.method == "GET":
        movies = request.db_session.query(Movie).limit(10)
        if request.user.is_focus:
            featured_movie = request.db_session.query(FeaturedMovie)\
                .filter_by(company_id=1, is_active=True).all()
        else:
            company = request.user.company
            # featured = request.db_session
            #     .query(FeaturedMovie).filter_by(company_id=company.id).all()
            featured_movie = company.featured_movies\
                .join(FeaturedMovie).filter_by(is_active=True).all()
        data = {
            'movies': movies,
            'featured': featured_movie,
        }
        return render(request, 'movies_featured.html', data)
    else:
        raise Http404


@login_required
@permission_required('movies_edit_featured')
def unfeature(request, movie_id):
    company = request.user.company
    featured = request.db_session.query(FeaturedMovie)\
        .filter_by(movie_id=movie_id)\
        .filter_by(company_id=company.id).first()
    featured.is_active = False
    return HttpResponseRedirect(reverse('movies.views.featured'))


@login_required
@permission_required('movies_edit_featured')
def short_info(request, movie_id):
    movie = request.db_session.query(Movie).filter_by(id=movie_id).first()
    is_featured = movie.featured \
        .filter(FeaturedMovie.company == request.user.company).first()
    if_featured = bool(is_featured and is_featured.is_active)
    render_data = {
        'movie': movie,
        'if_featured': if_featured,
    }
    return render(request, 'movie_short_info.html', render_data)
