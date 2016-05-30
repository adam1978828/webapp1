# -*- coding: utf-8 -*-
from django.conf.urls import url


__author__ = 'D.Kalpakchi'


urlpatterns = [
    url(r'^index/$', 'test_app.views.index'),
    url(r'^print/$', 'test_app.views.print_request'),
    url(r'^json/(.*)/$', 'test_app.views.json_resp'),
    url(r'^(.*)/$', 'test_app.views.test'),
]
