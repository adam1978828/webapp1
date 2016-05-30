# -*- coding: utf-8 -*-
from django.conf.urls import url
from price_plans import views

__author__ = 'D.Kalpakchi'


urlpatterns = [
    url(r'^$', 'price_plans.views.all_price_plans'),
    url(r'^add/$', 'price_plans.views.add_price_plan'),
    url(r'^edit/(?P<tariff_plan_id>\d+)/$', 'price_plans.views.edit_price_plan'),
    url(r'^show/(?P<tariff_plan_id>\d+)/$', 'price_plans.views.show_price_plan'),
]
