# -*- coding: utf-8 -*-
import codecs
import csv
import os
import time
import hashlib

import requests
from dateutil import parser as dp
from sqlalchemy.orm.exc import NoResultFound
import tmdbsimple as tmdb
from django.conf import settings

from Model import UPC, Movie, MovieTranslation, MovieGenreTranslation, UpdateMoviesStatsAlt
from Model import UpcMovie, DiskFormat, Language, MovieRating, MovieGenre
from .utils import init_logger, compare_optimize, search_optimize, download_archive, extract_zip_archive
import validator
from validator import MovieDataValidator
import sets
import omdb


__author__ = u'D.Ivanets, D.Kalpakchi'
tmdb.API_KEY = '83b91371cf3596807811c2e4c936f239'

log = init_logger()


def get_or_create_genre(session, genre_name):
    genre_name = genre_name.lower()
    try:
        genre = session.query(MovieGenre)\
                       .join(MovieGenreTranslation)\
                       .filter_by(value=genre_name).one()
    except NoResultFound:
        genre = MovieGenre()
        genre_t = MovieGenreTranslation(genre, value=genre_name)
        genre_t.language_id = 1
        session.add_all([genre, genre_t])
    return genre


def update_picture(movie, m_rec, picture_type='poster_path'):
    """Updates picture from tmdb response
    :param movie: Movie, that requires update
    :type movie: Movie
    :param m_rec: Movie record from tmdb
    :param picture_type: whether it is poster or backdrop.
    """
    picture_name = m_rec.get(picture_type)

    if not picture_name:
        return

    if picture_type == 'poster_path':
        path_pattern = 'poster{}'
        movie.img_path = picture_name
    else:
        path_pattern = 'backdrop{}'
        movie.bd_path = picture_name

    picture_url = 'http://image.tmdb.org/t/p/original{}'.format(picture_name)
    resp = requests.get(picture_url, stream=True)

    if resp.status_code == 200:
        picture_path = path_pattern.format(m_rec[picture_type])
        picture_full_path = os.path.join(settings.MEDIA_ROOT,
                                         'movie',
                                         picture_path)
        with open(picture_full_path, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
            f.close()


def update_movies_images():
    """Updates movie covers and backdrops for all movies.
     Used to improve pictures quality on server.
    """
    # initialize database session
    session = settings.SESSION()
    movies = session.query(Movie).all()

    for movie in movies:
        if movie.tmdb_id:
            yield "Updating images for movie #%d<br>" % movie.id

            try:
                m_rec = tmdb.Movies(int(movie.tmdb_id)).info(language='en')
            except Exception as e:
                yield "<font color='red'>%s</font>" % e.message
                continue

            update_picture(movie, m_rec, picture_type='poster_path')
            update_picture(movie, m_rec, picture_type='backdrop_path')

            yield "Images for movie #%d were successfully updated<br><br><br>" % movie.id
        else:
            yield "Movie #%d does not have TMDB id<br><br><br>" % movie.id

    session.commit()


def add_new_record(movie_data, m_rec_id, stats, session):
    """If we found a result in tmdb, this function called to add or
      update movie record in db.

    :param movie_data:
    :param m_rec_id:
    :param stats:
    :param session:
    :return:
    """

    # Get all info about movie from tmdb
    m_rec = tmdb.Movies(m_rec_id).info(language='en')

    # Try to find record with this movie in our db
    try:
        movie = session.query(Movie).filter_by(tmdb_id=m_rec['id']).one()
        m_t = session.query(MovieTranslation).filter_by(language_id=1).filter_by(movie=movie).one()
    except NoResultFound:
        # No results found in db, create new record
        movie = Movie()
        movie.tmdb_id = m_rec['id']
        m_t = MovieTranslation()
        m_t.language_id = 1
        m_t.movie = movie
        session.add_all([movie, m_t])

    # Here we start saving info about this movie.
    m_t.name = m_rec['title']
    m_t.description = m_rec['overview']
    movie.movie_translation.append(m_t)

    # Save movie cover and backdrop
    if not movie.img_path:
        update_picture(movie, m_rec, 'poster_path')
    if not movie.bd_path:
        update_picture(movie, m_rec, 'backdrop_path')

    movie.length = m_rec['runtime']
    movie.release_year = movie_data['Year'] if movie_data['Year'].isdigit() else None

    movie.movie_genre = []
    if 'release_date' in m_rec:
        movie.dt_release = dp.parse(m_rec['release_date'])

    # Add genres
    for item in m_rec['genres']:
        try:
            genre = session.query(MovieGenre)\
                           .join(MovieGenreTranslation)\
                           .filter_by(value=item['name'].lower()).one()
        except NoResultFound:
            genre = MovieGenre()
            genre_t = MovieGenreTranslation(genre, value=item['name'].lower())
            genre_t.language_id = 1
            session.add_all([genre, genre_t])
        movie.movie_genre.append(genre)

    # Add movie rating
    try:
        rating = session.query(MovieRating).filter_by(value=movie_data['Rating']).one()
    except NoResultFound:
        rating = MovieRating(movie_data['Rating'])
        session.add(rating)
    movie.movie_rating = rating

    # Save this UPC and related data
    try:
        upc = session.query(UPC).filter_by(upc=movie_data['UPC']).one()
    except NoResultFound:
        upc = UPC()
        session.add(upc)

    upc.upc = movie_data['UPC']
    upc.hti_id = int(movie_data['ID'])
    upc.sound = [session.query(Language).filter_by(id=1).one()]
    upc_movie = UpcMovie(movie_data['UPC'], movie.id, 2 if 'Blu-ray' in movie_data['DVD_Title'] else 1)
    session.add_all([movie, upc_movie])

    # save dvd release date from tmdb
    if validator.is_valid_dvd_release(movie_data[u'DVD_ReleaseDate']):
        movie.dt_dvd_release = dp.parse(movie_data[u'DVD_ReleaseDate'])

    # get data from omdb
    omdb_data = get_by_imdb_id(m_rec[sets.IMDB_ID])
    if MovieDataValidator.is_valid_data(omdb_data, check_fields=sets.CHECK_FIELDS_OMDB, validator=validator.VALIDATOR_OMDB):
        # save omdb data
        movie.dt_dvd_release = dp.parse(omdb_data[sets.DVD_RELEASE_DATE])
        movie.imdb_rating = float(omdb_data[sets.IMDB_RATING])
        movie.imdb_id = omdb_data[sets.IMDB_ID]
        movie.box_office = omdb_data[sets.BOXOFFICE]
    session.add(movie)
    session.commit()


def update_record(movie_data, upc_movie, session):
    movie = upc_movie.movie

    # Get up_to_dated information from TMDB
    try:
        m_rec = tmdb.Movies(movie.tmdb_id).info(language='en')
    except Exception as e:
        tmdb_records = tmdb.Search() \
            .movie(query=search_optimize(movie_data['DVD_Title']),
                   language='en')
        if tmdb_records['total_results']:
            match = tmdb_records['results'][0]
            if compare_optimize(movie_data['DVD_Title']) == compare_optimize(match['original_title']):
                movie.tmdb_id = match['id']
                m_rec = tmdb.Movies(movie.tmdb_id).info(language='en')
            else:
                return False
        else:
            return False

    # Save movie cover and backdrop
    if not movie.img_path:
        update_picture(movie, m_rec, 'poster_path')
    if not movie.bd_path:
        update_picture(movie, m_rec, 'backdrop_path')

    # Save movie length
    movie.length = m_rec['runtime']

    # get data from omdb
    omdb_data = get_by_imdb_id(m_rec[sets.IMDB_ID])

    # Save movie release date
    movie.release_year = int(movie_data['Year'])
    if 'release_date' in m_rec:
        movie.dt_release = dp.parse(m_rec['release_date'])
        movie.release_year = movie.dt_release.year
    else:
        movie.dt_release = dp.parse('{}-1-1'.format(movie.release_year))

    # Save movie genres
    movie.movie_genre = []
    for item in m_rec['genres']:
        genre = get_or_create_genre(session, item[u'name'])
        movie.movie_genre.append(genre)

    # Save movie rating
    try:
        rating = session.query(MovieRating).filter_by(value=movie_data['Rating']).one()
    except NoResultFound:
        rating = MovieRating(movie_data['Rating'])
        session.add(rating)
    movie.movie_rating = rating

    # save dvd release date from tmdb
    if validator.is_valid_dvd_release(movie_data[u'DVD_ReleaseDate']):
        movie.dt_dvd_release = dp.parse(movie_data[u'DVD_ReleaseDate'])
    # check fields
    if MovieDataValidator.is_valid_data(omdb_data, check_fields=sets.CHECK_FIELDS_OMDB, validator=validator.VALIDATOR_OMDB):
        # save omdb data
        movie.dt_dvd_release = dp.parse(omdb_data[sets.DVD_RELEASE_DATE])
        movie.imdb_rating = float(omdb_data[sets.IMDB_RATING])
        movie.imdb_id = omdb_data[sets.IMDB_ID]
        movie.box_office = omdb_data[sets.BOXOFFICE]

    session.add(movie)
    session.commit()
    return True


def filter_tmdb_search_results(csv_record, search_results):
    """This function provides filtering on search results in tmdb, based
     on optimized movie name
    :param search_results: List of results
    :type search_results: list
    :return: List of most successful results (preferably one)
    :rtype: list
    """
    # Start filtering results
    success_match = []
    movie_title_optimized = compare_optimize(csv_record['DVD_Title'])
    # We have some results
    for res in search_results:
        # Here we filter results, comparing optimized movie titles
        titles = (compare_optimize(res['title']),
                  compare_optimize(res['original_title']))
        if movie_title_optimized in titles:
            # Here we filter really old movies
            if res['release_date']:
                if dp.parse(res['release_date']).year >= 2000:
                    success_match.append(res)
            else:
                success_match.append(res)

    # Filter by release year
    if len(success_match) > 1:
        res = []
        for r in success_match:
            if r['release_date'] and abs(int(csv_record['Year']) - dp.parse(r['release_date']).year) < 2:
                res.append(r)
        success_match = res

    if len(success_match) > 1:
        res = []
        for r in success_match:
            if int(csv_record['Year']) == dp.parse(r['release_date']).year:
                res.append(r)
        success_match = res

    # If we still have multiple results, we just get the most popular
    if len(success_match) > 1:
        res = [success_match[0]]
        for r in success_match:
            if r['vote_count'] > res[0]['vote_count']:
                res = [r]
            elif r['vote_count'] == res[0]['vote_count'] and r != res[0]:
                res.append(r)
        success_match = res

    return success_match


def get_by_imdb_id(imdb_id):
    # get omdb data by imdb_id
    #NOTICE! set tomatos by default True
    # url = 'http://www.omdbapi.com'
    # json_data = {
    #     u'i': imdb_id,
    #     u'tomatoes':True,
    #     u'plot':'short',
    #     u'r':'json',
    # }
    # url += u'?i={id}&plot=short&r=json&tomatoes=true'
    result = dict().fromkeys(sets.OMDB_FIELDS)
    # movie_data = omdb.imdbid(imdb_id)
    # for field in sets.OMDB_FIELDS:
    #     result[field] = movie_data.get(field)
    return result


def update_db(session, stats):
    tmdb.API_KEY = '83b91371cf3596807811c2e4c936f239'
    tmdb_search = tmdb.Search()
    # session = settings.SESSION()
    # stats = UpdateMoviesStatsAlt()
    # session.add(stats)

    omdb.set_default('tomatoes', True)
    # Downloading archive
    stats.status = 1
    file_path = download_archive()

    # Extracting archive
    stats.status = 2
    csv_path = extract_zip_archive(file_path)

    # Open csv file and start parsing
    stats.status = 3
    csv_file = codecs.open(csv_path, mode='rb')
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_headers = csv_reader.next()

    i = 0
    err = 0
    success = 0
    added = 0
    existed = stats.existed
    data_validator = MovieDataValidator(None)
    # omdb_data = dict().fromkeys(sets.OMDB_FIELDS)
    movie_data = dict().fromkeys(csv_headers)
    header_indexes = dict().fromkeys(csv_headers)
    for header in csv_headers:
        header_indexes[header] = csv_headers.index(header)

    for row in csv_reader:
        row = [x.decode('unicode-escape') for x in row]
        for header in csv_headers:
            movie_data[header] = row[header_indexes[header]]
        data_validator.set_data(movie_data)
        if data_validator.is_valid():
            i += 1
            existed, err, success, added = process_row(session, movie_data, existed, tmdb_search, i, err, success, added)
            stats.detected = i
            stats.existed = existed
            stats.stored = success
            stats.not_recognized = err
            session.commit()
    return stats.existed, err, success


def process_row(session, movie_data, existed, tmdb_search, i, err, success, n):
    for k in range(5):
        try:
            # Looking for a record with such UPC code in our DB
            db_record = session.query(UpcMovie).get(movie_data[sets.UPC])
            if db_record and db_record.movie:
                existed += 1
                try:
                    update_record(movie_data, db_record, session)
                except Exception, ex:
                    print ex
                    err += 1
            else:
                # There is no record with such UPC code
                # Looking for a movie with such name in tmdb
                tmdb_records = tmdb_search.movie(query=search_optimize(movie_data['DVD_Title']), language='en')
                err, success, existed, n = process_tmdb_records(tmdb_records, movie_data, err, success, i, existed, session, n)
        except Exception as ex:
            err += 1
            time.sleep(2)
        return existed, err, success, n


def process_tmdb_records(tmdb_records, movie_data, err, success, i, existed, session, n):
    if tmdb_records['total_results']:
        # There are some search results in tmdb
        success_match = filter_tmdb_search_results(movie_data, tmdb_records['results'])

        if len(success_match) == 1:
            if not success_match[0]['release_date']:
                # We don't accept records without release date
                err += 1
            elif not success_match[0]['poster_path']:
                # We don't accept record without cover picture
                err += 1
            else:
                # Successfully found result
                success += 1
                n += 1
                add_new_record(movie_data, success_match[0]['id'], (i, existed, err, success), session)
        elif len(success_match) == 0:
            # There are no any matching results
            err += 1
        else:
            # There are still multiple results found after filtering.
            n += 1
    else:
        # No results were found in tmdb
        err += 1

    return err, success, existed, n


def update_poster_image_file_hash(session, stats):
    movies = session.query(Movie).filter(Movie.img_path != None).all()

    for val in movies:
        # TODO: pass full path except img_path
        full_path = os.path.join(settings.MEDIA_ROOT, 'movie', 'poster', val.img_path.strip('/'))
        val.hash = get_hash(full_path)
        session.add(val)
        session.commit()
        stats.hash_handled += 1


def get_hash(full_path):
        if not os.path.isfile(full_path):
            return None
        movie_file = open(full_path)
        movie_hash = hashlib.md5(movie_file.read()).hexdigest()

        return movie_hash