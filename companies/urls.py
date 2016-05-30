# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns


__author__ = 'D.Kalpakchi'


urlpatterns = patterns('companies.views',
    url(r'^add/$', 'add'),  # company_add
    url(r'^edit/$', 'edit'),  # company_edit_own
    url(r'^edit/(.*)/$', 'edit_by_id'),       # company_edit_any
    url(r'^list/$', 'view_list'),  # company_view_any
    url(r'^view/$', 'view'),  # company_view_own
    url(r'^view/(.*)/$', 'view_by_id'),       # company_view_any
    url(r'^staff/$', 'staff_list'),  # user_view
    url(r'^staff_focus/$', 'staff_list_focus'),  # focus_user_view
    url(r'^user_management/$', 'user_management'),  # client user_view
    url(r'^user_info/(.*)/$', 'user_info_by_id'),  # user_info
    # user_view, company_view_any
    url(r'^staff/(.*)/$', 'staff_list_by_id'),

    url(r'^upload/$', 'upload'),  # user_view
    # user_view
    url(r'^upload_archive/$', 'ajax_upload_archive'),

    # url(r'^company/ajax_add_company/$', views.ajax_add_company),
    # url(r'^company/ajax_change_logo/$', company.ajax_change_logo),
    url(r'^settings/$', 'settings'),
    url(r'^settings_list/$', 'settings_list'),
    # url(r'^company_settings/(.*)/$', 'company_settings'),
    url(r'^permissions/$', 'permissions'),
    url(r'^(?P<company_id>\d+)/permissions/remove/(?P<user_id>\S+)/$', 'remove_permission'),
    url(r'^(?P<company_id>\d+)/permissions/$', 'permissions'),
    url(r'^(?P<company_id>\d+)/permissions/add/$', 'add_permission'),

    url(r'^group_list/$', "group_list"),
    url(r'^group_add/$', "group_add"),
    url(r'^group_remove/(?P<group_id>\S+)/$', 'remove_group'),
    url(r'^group_edit/(?P<group_id>\S+)/$', 'edit_group'),
    url(r'^group_save/(?P<group_id>\S+)/$', 'save_group'),

    url(r'^sites/$', 'sites'),
    url(r'^trailers/$', 'trailers'),
    url(r'^trailers/add/$', 'add_trailer'),
    url(r'^trailers/remove/(.*)/$', 'remove_trailer'),
    url(r'^trailers/edit/(.*)/$', 'edit_trailer'),
    url(r'^trailers/save/$', 'ajax_edit_trailer'),
    url(r'^social/$', 'social'),
    url(r'^social/(?P<social_id>\d+)/remove$', 'social_remove'),
    url(r'^send_mail_for_password_restore/$', 'send_mail_for_password_restore'),

    # For focus and company
    url(r'^(?P<company_id>\d+)/sites/$', 'company_sites'),
    url(r'^(?P<company_id>\d+)/company_settings/$', 'company_settings'),
    url(r'^(?P<company_id>\d+)/company_sites/save/$', 'ajax_save_company_sites'),
)
