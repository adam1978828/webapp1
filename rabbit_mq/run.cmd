set DJANGO_SETTINGS_MODULE=WebApp.settings.dev
celery -A rabbit worker &
pause