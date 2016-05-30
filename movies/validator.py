# -*- coding: utf-8 -*-
__author__ = 'p.nevmerzhitskyi'

import sets
import dateutil.parser

# validators for tmdb data
def is_valid_genre(value=None):
    genres = [genre.strip() for genre in value.split(',')]
    return any([genre not in sets.GENRE_STOP for genre in genres])


def is_valid_upc(value):
    return value


def is_valid_status(value):
    return value in sets.STATUS_OK


def is_valid_year(value):
    return value.isdigit() and int(value) > sets.MIN_YEAR


def is_valid_dvd_title(value):
    return not ('Vol. ' in value) and ('Collector\'s Edition' in value)

# validators for omdb data
def is_valid_imdb_rating(value):
    try:
        float(value)
        return True
    except Exception, e:
        return False


def is_valid_dvd_release(value):
    try:
        dateutil.parser.parse(value)
        return True
    except Exception, e:
        return False


def is_valid_imdb_id(value):
    return value

def is_valid_boxoffice(value):
    return value

VALIDATOR_TMDB = {
    sets.GENRE: is_valid_genre,
    sets.UPC: is_valid_upc,
    sets.STATUS: is_valid_status,
    sets.YEAR: is_valid_year,
    sets.DVD_TITLE: is_valid_dvd_title,
}

VALIDATOR_OMDB = {
    sets.IMDB_RATING: is_valid_imdb_rating,
    sets.DVD_RELEASE_DATE: is_valid_dvd_release,
    sets.IMDB_ID: is_valid_imdb_id,
    sets.BOXOFFICE: is_valid_boxoffice,
}

class MovieDataValidator(object):

    def __init__(self, data, check_fields=None, validator=None):
        self.data = data
        self.validator = VALIDATOR_TMDB
        self.check_fields = sets.CHECK_FIELDS_TMDB
        if check_fields:
            self.check_fields = check_fields
        if validator:
            self.validator.update(validator)

    def set_data(self, data):
        self.data = data

    def is_valid(self):
        for field in self.check_fields:
            if not self.is_valid_field(field):
                return False
        return True

    @classmethod
    def is_valid_data(cls, data, check_fields=None, validator=None):
        validator_obj = cls(data, check_fields, validator)
        return validator_obj.is_valid()

    def is_valid_field(self, field):
        return self.validator[field](value=self.data[field])