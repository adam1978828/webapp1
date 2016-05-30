from django.conf.urls import url, patterns

__author__ = 'D.Kalpakchi'


urlpatterns = patterns('deals.views',
    url(r'^$', 'all_deals'),
    url(r'^json_deals/$', 'json_deals'),
    url(r'^json_deals/(?P<disk_rf_id>\S+)/$', 'json_deals'),
    url(r'^deal/(.*)/$', 'deal_by_id'),
    url(r'^(?P<deal_id>\S+)/void/$', 'finish_deal_void'),
    url(r'^(?P<deal_id>\S+)/finish/$', 'finish_deal'),    
    url(r'^(?P<deal_id>\S+)/change/$', 'manual_change'),
    url(r'^(?P<deal_id>\S+)/$', 'show_deal')
)