# -*- coding: utf-8 -*-
__author__ = 'p.nevmerzhitskyi'

GENRE = 'Genre'
UPC = 'UPC'
STATUS = 'Status'
YEAR = 'Year'
DVD_TITLE = 'DVD_Title'
MIN_YEAR = 2000

GENRE_STOP = ['Software', 'Ballet', 'Silent', 'Sports', 'Exercise', 'Karaoke',
              'Opera', 'Games', 'Special Interest', 'Drama/Silent', 'Music',
              'Dance/Ballet', 'Late Night', 'TV Classics']

STATUS_OK = ['Pending', 'Out']

CHECK_FIELDS_TMDB = [GENRE, UPC, STATUS, YEAR]

# imdb fields
IMDB_RATING = u'imdb_rating'
DVD_RELEASE_DATE = u'dvd'
IMDB_ID = u'imdb_id'
BOXOFFICE = u'box_office'

CHECK_FIELDS_OMDB = [IMDB_RATING, IMDB_ID, DVD_RELEASE_DATE, BOXOFFICE]

OMDB_FIELDS = [IMDB_RATING, DVD_RELEASE_DATE, IMDB_ID, BOXOFFICE]
OMDB_DATA = dict().fromkeys(OMDB_FIELDS)