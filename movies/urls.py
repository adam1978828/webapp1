from django.conf.urls import patterns, url
from django.conf import settings

__author__ = "D.Kalpakchi"


urlpatterns = patterns(
    'movies.views',
    url(r'^all/$', 'all'),
    url(r'^json_all/$', 'json_all'),
    url(r'^(?P<mode>\b(add|edit)\b)/(?P<movie_id>\d+|)$', 'add_edit'),
    url(r'^add/$', 'add_edit'),
    url(r'^add_upc/$', 'add_upc'),
    url(r'^search/$', 'search'),
    url(r'^search/by/title$', 'search_by_title'),

    url(r'^update/center/\b(full_load|hash_update|log)\b$', 'update_center_alt'),
    url(r'^update/center/logs/$', 'json_update_center_log'),
    url(r'^update/center/refresh/$', 'refresh_update_center'),

    url(r'^featured/$', 'featured'),
    url(r'^featured/(?P<movie_id>\d+)/unfeature/$', 'unfeature'),
    url(r'^(?P<movie_id>\d+)/short_info/$', 'short_info')
)


# if settings.DEBUG:
urlpatterns += patterns('movies.views',
    url(r'^update/images/$', 'update_images')
)