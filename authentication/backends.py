# -*- coding: utf-8 -*-
from Model import User
from sqlalchemy.orm.exc import NoResultFound
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from libs.validators.core import validation_error

__author__ = 'tegelman'


class EmailBackend(object):

    """
    Class provides user authentication using email as a login
    """
    supports_anonymous_user = True
    supports_inactive_user = True

    def __init__(self):
        self.session = settings.SESSION()


    def authenticate(self, username=None, password=None, user_type=[2, 3], errors=[], company_id=None):
        try:
            validate_email(username)
        except ValidationError:
            errors.append(validation_error('email', 'Invalid email'))
            return None
            
        try:
            user = self.session.query(User)\
                .filter(User.user_type_id.in_(user_type))\
                .filter_by(email=username)
            if company_id:
                user = user.filter(User.company_id == company_id)
            user = user.one()
        except NoResultFound:
            errors.append(validation_error('email', 'Your email is incorrect'))
            return None

        if user.is_pass_valid(password):
            return user
        else:
            errors.append(validation_error('password', 'Your password is incorrect'))
            return None

    def get_user(self, user_id):
        try:
            user = self.session.query(User).filter_by(id=user_id).one()
        except NoResultFound:
            return None

        return user
