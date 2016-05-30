set DJANGO_SETTINGS_MODULE=WebApp.settings.dev
celery -A cron beat -l debug -f beat.log &
pause