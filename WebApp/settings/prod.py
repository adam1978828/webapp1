# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from django.utils.translation import ugettext_lazy as _

from .base import *


__author__ = 'Denis Ivanets (denself@gmail.com)'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

# Database
DB_HOST = 'intdb.focusintense.com'
# DB_HOST = '192.168.151.143'
DB_NAME = 'kiosk_global_test'
DB_USER = 'kiosk'
DB_PASS = 'XLc2v3B8tUv7ApagAnifEg1'
DB_PORT = '5432'

DATABASE = "postgresql://{}:{}@{}:{}/{}"
DATABASE = DATABASE.format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT
    }
}

engine = create_engine(DATABASE)
SESSION = sessionmaker(bind=engine)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGES = (
    ('en', _('English')),
)

# Static files (CSS, JavaScript, Images)

MEDIA_URL = '/media/'

SCREEN_TOP_URL = '%sscreenshot/top/' % MEDIA_URL
SCREEN_BOT_URL = '%sscreenshot/bottom/' % MEDIA_URL


ADMINS = (('D.Ivanets', 'd.ivanets@kit-xxi.com.ua'),
          ('O.Tegelman', 'o.tegelman@kit-xxi.com.ua'),
          ('P.Nevmerzhytskyi', 'p.nevmerzhytskyi@kit-xxi.com.ua'),
          ('M.Kladivo', 'mkladivo@pccentral.us'))

# SMTP server settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'spamfilterinside.pccentral.us'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'FIC-NOREPLY'
EMAIL_HOST_PASSWORD = 'Back1nSaddle!@!'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@focusintense.com'
SERVER_EMAIL = 'noreply@focusintense.com'

# JASPER REPORTS CONFIG
JASPER_USERNAME = 'jasperadmin'
JASPER_PASSWORD = 'jasperadmin'
JASPER_HOST = 'http://reports.focusintense.com'
JASPER_CONTEXT_NAME = 'jasperserver'
JASPER_PORT = '8080'
JASPER_AUTH_COOKIE_EXP = 120
JASPER_CACHE_REPORT_PARAMS = True
JASPER_CACHE_REPORT_TIMEOUT = 86400