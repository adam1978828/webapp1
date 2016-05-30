# -*- coding: utf-8 -*-
import os
from django.template.base import add_to_builtins

__author__ = 'Denis Ivanets (denself@gmail.com)'


add_to_builtins('WebApp.templatetags.filters')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vqv!q5@kju1yaf=^@)hcay%j7e6!9mvj0_l_$y(7g6+*rm=j8c'

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'authentication',
    'acc',
    'kiosk_api',
    'price_plans',
    'companies',
    'test_app',
    'kiosks',
    'WebApp',
    'rental_fleets',
    'deals',
    'payments',
    'profiles',
    'movies',
    'sites',
    'coupons',
    'reports_views',
    'dashboard'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'WebApp.middleware.SQLAlchemySessionMiddleware',
    'WebApp.middleware.SiteMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'WebApp.middleware.SQLAlchemyAuthMiddleware',
    'WebApp.middleware.ServerStateMiddleware',
    'WebApp.middleware.KioskApiMiddleware',
    'WebApp.middleware.PostgreAuditMiddleware',
)

ROOT_URLCONF = 'WebApp.urls'

WSGI_APPLICATION = 'WebApp.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'

LOCALE_PATHS = (
    '/authentication/locale',
)

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates'), ]

TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader')

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)


AUTHENTICATION_BACKENDS = (
    'authentication.backends.EmailBackend',
)

# Settings to store sessions in local folder

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

SESSION_FILE_PATH = os.path.join(BASE_DIR, 'sessions')
if not os.path.exists(SESSION_FILE_PATH):
    os.makedirs(SESSION_FILE_PATH)

LOGIN_URL = "/auth/login/"

TMDB_API_KEY = '83b91371cf3596807811c2e4c936f239'

TEMP_DIR = os.path.join(BASE_DIR, 'temp')
LOCAL_DIR = os.path.join(BASE_DIR, 'local')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
REPORTS_ROOT = os.path.join(BASE_DIR, 'reports')
KIOSK_DB_DIR = os.path.join(TEMP_DIR, 'local_dbs')

LINKPOINT_KEYS_DIR = os.path.join(LOCAL_DIR, 'payment_system/linkpoint/keys')
INSTALLER_DIR = os.path.join(LOCAL_DIR, 'installer')

DISK_PHOTO_DIR = os.path.join(MEDIA_ROOT, 'disk_photo')
SCREENSHOT_DIR = os.path.join(MEDIA_ROOT, 'screenshot')
VIDEO_DIR = os.path.join(MEDIA_ROOT, 'video')
SCREEN_TOP_DIR = os.path.join(SCREENSHOT_DIR, 'top')
SCREEN_BOT_DIR = os.path.join(SCREENSHOT_DIR, 'bottom')
POSTER_DIR = os.path.join(MEDIA_ROOT, 'movie/poster')


for d in [TEMP_DIR, LOCAL_DIR, LINKPOINT_KEYS_DIR, INSTALLER_DIR,
          DISK_PHOTO_DIR, SCREENSHOT_DIR, SCREEN_TOP_DIR, SCREEN_BOT_DIR,
          VIDEO_DIR, LOGS_DIR, KIOSK_DB_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

SMART_REPORT_DB_ENGINE = 'SQLAlchemy'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'handlers': {
        # Include the default Django email handler for errors
        # This is what you'd get without configuring logging at all.
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'filters': ['require_debug_false'],
             # But the emails are plain text by default - HTML is nicer
            'include_html': True,
        },
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/filename.log')
        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}