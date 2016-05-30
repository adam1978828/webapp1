# -*- coding: utf-8 -*-
import csv
import datetime as dt
import os
import time

import requests
from dateutil import parser as dp
from sqlalchemy.orm.exc import NoResultFound
import tmdbsimple as tmdb
from django.conf import settings
from django.template.loader import render_to_string

from Model import UPC, Movie, MovieTranslation, MovieGenreTranslation
from Model import UpcMovie, DiskFormat, Language, MovieRating, MovieGenre
from .utils import init_logger, send_message, compare_optimize, search_optimize, download_archive, extract_zip_archive


__author__ = u'D.Ivanets, D.Kalpakchi'
tmdb.API_KEY = '83b91371cf3596807811c2e4c936f239'


log = init_logger()


def update_picture(movie, m_rec, picture_type='poster_path'):
    """Updates picture from tmdb response
    :param movie: Movie, that requires update
    :type movie: Movie
    :param m_rec:
    :param picture_type:
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


def add_new_record(d, m_rec_id, stats, session):
    """If we found a result in tmdb, this function called to add or
      update movie record in db.

    :param d:
    :param m_rec_id:
    :param stats:
    :param session:
    :return:
    """
    from Model import UpdateMoviesStats

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
    movie.release_year = d['Year'] if d['Year'].isdigit() else None

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
        rating = session.query(MovieRating).filter_by(value=d['Rating']).one()
    except NoResultFound:
        rating = MovieRating(d['Rating'])
        session.add(rating)
    movie.movie_rating = rating

    # Save this UPC and related data
    try:
        upc = session.query(UPC).filter_by(upc=d['UPC']).one()
    except NoResultFound:
        upc = UPC()
        session.add(upc)

    upc.upc = d['UPC']
    upc.hti_id = int(d['ID'])
    upc.sound = [session.query(Language).filter_by(id=1).one()]
    upc_movie = UpcMovie(d['UPC'], movie.id, 2 if 'Blu-ray' in d['DVD_Title'] else 1)
    session.add_all([movie, upc_movie])
    if not stats[0] % 10:
        detected, existed, not_recognized, stored = stats
        stats = UpdateMoviesStats(detected, existed, not_recognized, stored, 'partial')
        session.add(stats)
        session.commit()


def update_record(d, upc_movie, session):
    movie = upc_movie.movie
    response = render_to_string('movie_in_db_log.html', {
        'movie': d['DVD_Title'],
        'id': movie.id,
        'need_update': True,
        'color': 'green',
        'message': 'UPDATED'
    })
    try:
        m_rec = tmdb.Movies(movie.tmdb_id).info(language='en')
    except Exception as e:
        tmdb_records = tmdb.Search().movie(query=search_optimize(d['DVD_Title']), language='en')
        if tmdb_records['total_results']:
            match = tmdb_records['results'][0]
            if compare_optimize(d['DVD_Title']) == compare_optimize(match['original_title']):
                movie.tmdb_id = match['id']
                m_rec = tmdb.Movies(movie.tmdb_id).info(language='en')
                response = render_to_string('movie_in_db_log.html', {
                    'movie': d['DVD_Title'],
                    'id': movie.id,
                    'need_update': True,
                    'wrong': True,
                    'error': 'WRONG TMDB ID. UPDATING...',
                    'color': 'green',
                    'message': 'UPDATED'
                })
            else:
                return render_to_string('movie_in_db_log.html', {
                    'movie': d['DVD_Title'],
                    'id': movie.id,
                    'need_update': True,
                    'wrong': True,
                    'error': 'Wrong TMDB id. Updating...',
                    'color': 'red',
                    'message': 'NO EXACT MATCH'
                })
        else:
            return render_to_string('movie_in_db_log.html', {
                'movie': d['DVD_Title'],
                'id': movie.id,
                'need_update': True,
                'wrong': True,
                'error': 'Wrong TMDB id. Updating...',
                'color': 'red',
                'message': 'NO MATCH'
            })

    # Save movie cover and backdrop
    if not movie.img_path:
        update_picture(movie, m_rec, 'poster_path')
    if not movie.bd_path:
        update_picture(movie, m_rec, 'backdrop_path')

    movie.length = m_rec['runtime']
    movie.release_year = d['Year'] if d['Year'].isdigit() else None
    movie.movie_genre = []
    if 'release_date' in m_rec:
        movie.dt_release = dp.parse(m_rec['release_date'])

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
    try:
        rating = session.query(MovieRating).filter_by(value=d['Rating']).one()
    except NoResultFound:
        rating = MovieRating(d['Rating'])
        session.add(rating)
    movie.movie_rating = rating
    movie.dt_modify = dt.datetime.utcnow()
    session.add(movie)
    session.commit()
    return response


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


def update_db():
    import codecs
    
    tmdb.API_KEY = '83b91371cf3596807811c2e4c936f239'
    s = tmdb.Search()
    session = settings.SESSION()

    genre_stop = ['Software', 'Ballet', 'Silent', 'Sports', 'Exercise', 'Karaoke', 'Opera', 'Games', 'Special Interest',
                  'Drama/Silent', 'Music', 'Dance/Ballet', 'Late Night', 'TV Classics']
    status_ok = ['Pending', 'Out']

    # Downloading archive
    send_message(u"<p data-id='log'>Downloading archive... <br></p>;@0;@0;@0;@0@$@")
    file_path = download_archive()

    # Extracting archive
    send_message(u"<p data-id='log'>Download is finished. Extracting file...<br></p>;@0;@0;@0;@0@$@")
    csv_path = extract_zip_archive(file_path)

    # Open csv file and start parsing
    send_message(u"<p data-id='log'>Extracting is finished. Updating db...<br></p>;@0;@0;@0;@0@$@")
    csv_file = codecs.open(csv_path, mode='rb')
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_headers = csv_reader.next()

    def generate_in_db_response(color, message, need_update=True, wrong=False, error=None):
        return render_to_string('movie_in_db_log.html', {
            'movie': d['DVD_Title'],
            'id': db_record.movie_id,
            'need_update': need_update,
            'wrong': wrong,
            'error': error,
            'color': color,
            'message': message
        })

    def generate_not_in_db_response(color, message, movie=None, found=None, level=None):
        if level:
            log.log(level, message)
        result = render_to_string('movie_not_in_db_log.html', {
            'movie': d['DVD_Title'] if movie is None else movie,
            'found': ", ".join(map(lambda dd: dd['title'], tmdb_records['results'])) if found is None else found,
            'color': color, 
            'message': message
        })
        result += ';@%d;@%d;@%d;@%d@$@' % (i, in_db, err, success)
        send_message(result)

    i = n = success = in_db = err = 0
    for row in csv_reader:
        row = [x.decode('unicode-escape') for x in row]

        d = dict(zip(csv_headers, row))
        if d['Genre'] not in genre_stop\
                and d['UPC'] \
                and d['Status'] in status_ok \
                and (d['Year'].isdigit() and int(d['Year']) > 2000) \
                and not 'Vol. ' in d['DVD_Title'] \
                and not 'Collector\'s Edition' in d['DVD_Title']:
            i += 1
            while True:
                try:
                    # Looking for a record with such UPC code in our DB
                    db_record = session.query(UpcMovie).filter_by(upc=d['UPC']).first()
                    if db_record and db_record.movie:
                        in_db += 1
                        if 'Updated' in d and int(d['Updated']):
                            # This should filter recently updated records
                            if (dt.datetime.utcnow() - db_record.dt_modify).days < 1:
                                response = generate_in_db_response('green', 'UP TO DATE')
                            else:
                                try:
                                    response = update_record(d, db_record, session)
                                except Exception, ex:
                                    response = generate_in_db_response('red', 'DB ERROR: %s' % (ex,))
                        else:
                            response = generate_in_db_response('#DAA520', 'ALREADY UP TO DATE', need_update=False)
                        response += ';@%d;@%d;@%d;@%d@$@' % (i, in_db, err, success)
                        send_message(response)
                    else:
                        # There is no record with such UPC code
                        # Looking for a movie with such name in tmdb
                        tmdb_records = s.movie(query=search_optimize(d['DVD_Title']), language='en')

                        if tmdb_records['total_results']:
                            # There are some search results in tmdb
                            success_match = filter_tmdb_search_results(d, tmdb_records['results'])

                            if len(success_match) == 1:
                                if not success_match[0]['release_date']:
                                    # We don't accept records without release date
                                    err += 1
                                    result_message = u'NO RELEASE DATE: {}'.format(d['DVD_Title'])
                                    generate_not_in_db_response('red', result_message, level=30)
                                elif not success_match[0]['poster_path']:
                                    # We don't accept record without cover picture
                                    err += 1
                                    result_message = u'NO COVER: {}'.format(d['DVD_Title'])
                                    generate_not_in_db_response('#DAA520', result_message, level=30)
                                else:
                                    # Successfully found result
                                    success += 1
                                    n += 1
                                    result_message = u'{} WAS SUCCESSFULLY ADDED'.format(d['DVD_Title'])
                                    add_new_record(d, success_match[0]['id'], (i, in_db, err, success), session)
                                    generate_not_in_db_response('green', result_message, level=20)
                            elif len(success_match) == 0:
                                # There are no any matching results
                                err += 1
                                result_message = u'NO COMPARES: {}'.format(d['DVD_Title'])
                                generate_not_in_db_response(u'#DAA520', result_message, level=30)
                            else:
                                # There are still multiple results found after filtering.
                                n += 1
                                result_message = u'{} RESULTS FOR: {}'.format(len(success_match), d['DVD_Title'])
                                generate_not_in_db_response(u'#DAA520', result_message, level=30)
                        else:
                            # No results were found in tmdb
                            err += 1
                            result_message = u'NO RESULTS FOUND: '.format(d['DVD_Title'])
                            generate_not_in_db_response('red', result_message, found=False, level=30)
                    break
                except Exception as ex:
                    err += 1
                    result_message = u'ERROR ON MOVIE "{}": {}'.format(d['DVD_Title'], ex.message)
                    generate_not_in_db_response('red', result_message, movie=False, found=False, level=30)
                    time.sleep(2)
    session.commit()
    send_message(u'-1')
    return i, in_db, err, success