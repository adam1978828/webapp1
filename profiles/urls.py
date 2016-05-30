from django.conf.urls import url, patterns


__author__ = 'D.Kalpakchi'

urlpatterns = patterns('profiles.views',
    url(r'^$', 'view'),                       # Both
    url(r'^view/(.*)/$', 'view_by_id'),       # user_view
    url(r'^add/$', 'add_staff'),  # user_add
    url(r'^edit/$', 'edit'),
    url(r'^edit/(.*)/$', 'edit_by_id'),  # user_edit
    url(r'^perms/(.*)/$', 'perms_by_id'),  # user_set_perms
)