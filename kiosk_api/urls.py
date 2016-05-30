# -*- coding: utf-8 -*-
from django.conf.urls import url

__author__ = u'D.Ivanets'


urlpatterns = [
    url(ur'^bash_result/$',         u'kiosk_api.views.bash_result'),
    url(ur'^check/$',               u'kiosk_api.views.check'),
    url(ur'^data_actualize/$',      u'kiosk_api.views.data_actualize'),
    url(ur'^data_download/$',       u'kiosk_api.views.data_download'),
    url(ur'^process_payments/$',    u'kiosk_api.views.process_payments'),
    url(ur'^pre_deal/$',            u'kiosk_api.views.pre_deal'),
    url(ur'^upload_screenshot/$',   u'kiosk_api.views.upload_screenshot'),
    url(ur'^upload_logs/$',         u'kiosk_api.views.upload_log_archive'),
    url(ur'^upload/archive/$',      u'kiosk_api.views.upload_archive'),
    url(ur'^check_authorization/$', u'kiosk_api.views.check_authorization'),
    url(ur'^get_script/$',          u'kiosk_api.views.get_script'),
    url(ur'^get_package/$',         u'kiosk_api.views.get_package'),
    url(ur'^get_test_package/$',    u'kiosk_api.views.get_package', {'test': True}),
    url(ur'^get_coupon/$',    u'kiosk_api.views.get_coupon'),
    url(ur'^get_reserv/$',    u'kiosk_api.views.get_reserv'),
    url(ur'^upload_local_db/$',         u'kiosk_api.views.upload_local_db'),
]