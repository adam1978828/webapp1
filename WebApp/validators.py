# -*- coding: utf-8 -*-
import re

__author__ = 'D.Ivanets'


def email_valid(email):
    return bool(re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+$", email))


def password_valid(password):
    return bool(re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password))
