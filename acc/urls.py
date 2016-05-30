# -*- coding: utf-8 -*-
from django.conf.urls import url
from views import permission

__author__ = 'D.Ivanets'


urlpatterns = [
    # perms_moderate_groups
    url(r'^permission/add_group/$', permission.add_group),
    # perms_moderate_group
    url(r'^permission/edit_group/(.*)/$', permission.edit_group)

    # url(r'^profile/ajax_save_profile/(.*)$', views.ajax_save_profile),
    # url(r'^', views.error),
]
