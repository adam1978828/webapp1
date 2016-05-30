# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from django.utils.translation import ugettext_lazy as _

from .base import *


__author__ = 'Denis Ivanets (denself@gmail.com)'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# Database
DB_HOST = '77.120.98.132'
# DB_HOST = '10.18.212.7'
DB_NAME = 'kiosk_global_dev'
# DB_NAME = 'kiosk_prod_db'
DB_USER = 'kiosk'
# DB_USER = 'postgres'
DB_PASS = 'kiosk'
# DB_PASS = 'postgres'
DB_PORT = '5432'
# DB_PORT = '5435'

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
    ('uk', _('Ukrainian')),
)

# Static files (CSS, JavaScript, Images)

MEDIA_URL = 'http://66.6.127.167/media/'

SCREEN_TOP_URL = '%sscreenshot/top/' % MEDIA_URL
SCREEN_BOT_URL = '%sscreenshot/bottom/' % MEDIA_URL


# SMTP server settings
ADMINS = (('D.Ivanets', 'd.ivanets@kit-xxi.com.ua'), ('p.nevmerzhytskyi', 'p.nevmerzhytskyi@kit-xxi.com.ua'))
# ADMINS = (('M.Kladivo', 'mkladivo@pccentral.us'), )

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = '587'
# EMAIL_HOST_USER = 'dvd.focus.kiosk.main@gmail.com'
# EMAIL_HOST_PASSWORD = 'naphazoline_new'
# EMAIL_USE_TLS = True


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'spamstopper.pccentral.us'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'FIC-NOREPLY'
EMAIL_HOST_PASSWORD = 'Back1nSaddle!@!'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@focusintense.com'
SERVER_EMAIL = 'noreply@focusintense.com'


# JASPER REPORTS CONFIG
JASPER_USERNAME = 'jasperadmin'
JASPER_PASSWORD = 'jasperadmin'
JASPER_HOST = 'http://10.18.212.7'
JASPER_CONTEXT_NAME = 'jasperserver'
JASPER_PORT = '8082'
JASPER_AUTH_COOKIE_EXP = 10
JASPER_CACHE_REPORT_PARAMS = True
JASPER_CACHE_REPORT_TIMEOUT = 30
JASPER_AUTO_LOGIN = False