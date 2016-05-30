from django.conf import settings
from django.shortcuts import redirect
from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^auth/', include('authentication.urls')),
    url(r'^acc/', include('acc.urls')),
    url(r'^kiosk_api/', include('kiosk_api.urls')),
    url(r'^priceplans/', include('price_plans.urls')),
    url(r'^company/', include('companies.urls')),
    url(r'^test/', include('test_app.urls')),
    url(r'^kiosks/', include('kiosks.urls')),
    url(r'^rentalfleet/', include('rental_fleets.urls')),
    url(r'^deals/', include('deals.urls')),
    url(r'^payments/', include('payments.urls')),
    url(r'^profile/', include('profiles.urls')),
    url(r'^movies/', include('movies.urls')),
    url(r'^coupons/', include('coupons.urls')),
    url(r'^reports/', include('reports_views.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^$', lambda request: redirect('/auth/login/')),
)

handler403 = 'acc.views.exceptions.error403'
handler404 = 'acc.views.exceptions.error404'

if settings.DEBUG:
    from django.views.generic import RedirectView
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        # url(r'^media/(?P<path>.*)$', RedirectView.as_view(url='http://66.6.127.167:8080/media/%(path)s/')),
    )
