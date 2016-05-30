# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns


__author__ = 'D.Kalpakchi'


urlpatterns = patterns('kiosks.views',
    url(r'^list/$', 'view_list'),  # company_add
    url(r'^edit/(?P<kiosk_id>\d+)/$', 'edit_by_id'),  # company_edit_own
    url(r'^ajax_add_kiosk/$', 'ajax_add_kiosk'),
    url(r'^(?P<kiosk_id>\d+)/settings/$', 'settings'),
    url(r'^add/$', 'add'),
    url(r'^(?P<kiosk_id>\d+)/tariffs/$', 'kiosk_tariff_plans'),
    url(r'^(?P<kiosk_id>\d+)/permissions/$', 'permissions'),
    url(r'^(?P<kiosk_id>\d+)/permissions/add/$', 'add_permission'),
    url(r'^(?P<kiosk_id>\d+)/permissions/remove/(?P<user_id>\S+)/$', 'remove_permission'),
    url(r'^(?P<kiosk_id>\d+)/tariffs/(?P<tariff_plan_id>\d+)/revert$', 'revert_tariff_values'),
    url(r'^(?P<kiosk_id>\d+)/tariffs/(?P<tariff_plan_id>\d+)/$', 'tariff_values'),
    url(r'^(?P<kiosk_id>\d+)/ajax_order_by/(?P<order_type_id>\d+)/$', 'ajax_order_by'),
    url(r'^(?P<kiosk_id>\d+)/ajax_review_inventory/(?P<review_type_id>\d+)/$', 'ajax_review_inventory'),
    url(r'^(?P<kiosk_id>\d+)/ajax_review_all/$', 'ajax_review_all'),
    url(r'^(?P<kiosk_id>\d+)/ajax_kill_review/(?P<review_id>\S+)/$', 'ajax_review_kill'),
    url(r'^(?P<slot_id>\d+)/ajax_disk_to_eject/(?P<is_to_eject>\d+)/$', 'ajax_disk_to_eject'),
    url(r'^(?P<kiosk_id>\d+)/slots/$', 'kiosk_slots'),
    url(r'^(?P<kiosk_id>\d+)/screens/$', 'screens'),
    url(r'^(?P<kiosk_id>\d+)/screens/make/$', 'make_screen'),
    url(r'^(?P<kiosk_id>\d+)/trailers/schedule/$', 'trailers_schedule'),
    url(r'^(?P<kiosk_id>\d+)/change_state/(?P<state>\d+)/$', 'ajax_disable'),

    url(r'^(?P<kiosk_id>\d+)/bash/$', 'kiosk_bash'),
    url(r'^(?P<kiosk_id>\d+)/ajax_bash/$', 'ajax_kiosk_bash'),

    url(r'^(?P<kiosk_id>\d+)/calibration/$', 'kiosk_calibration'),
    url(r'^(?P<kiosk_id>\d+)/ajax_calibration/$', 'ajax_kiosk_calibration'),

    url(r'^multi-settings/$', 'multi_settings'),
    url(r'^global_review_inventory/$', 'global_review_inventory'),

)
