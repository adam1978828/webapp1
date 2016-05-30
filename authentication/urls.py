# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.conf.urls import url
from authentication import views

__author__ = 'D.Ivanets'


urlpatterns = [
    url(r'^$', lambda x: HttpResponseRedirect("login")),
    url(r'^login/$', 'authentication.views.login'),
    url(r'^logout/$', 'authentication.views.logout'),
    url(r'^restore/code/(.*)/$', 'authentication.views.restore_code'),
    url(r'^restore/$', 'authentication.views.restore'),

    url(r'^test/$', views.test),

    url(r'^ajax_check_credentials',
        'authentication.views.ajax_check_credentials'),
    url(r'^ajax_check_email', 'authentication.views.ajax_check_email'),
    url(r'^ajax_change_password', 'authentication.views.ajax_change_password'),
    # url(r'^', views.error),
]
