from django.conf.urls import url, patterns

__author__ = 'D.Kalpakchi'


urlpatterns = patterns('dashboard.views',
    url(r'^$', 'all_charts')
)