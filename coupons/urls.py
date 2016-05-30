from django.conf.urls import url, patterns

__author__ = 'D.Kalpakchi'


urlpatterns = patterns(
    'coupons.views',
    url(r'^all/$', 'all_coupons'),
    url(r'^json_all/$', 'json_all'),
    url(r'^all/types/$', 'all_types'),
    url(r'^add/$', 'add'),
    url(r'^add/(?P<coupon_id>\d+)/$', 'add'),
    url(r'^remove/(?P<coupon_id>\d+)/$', 'remove'),
    url(r'^restore/(?P<coupon_id>\d+)/$', 'restore'),
    url(r'^(?P<coupon_id>\d+)/$', 'edit_coupon_by_id'),
)