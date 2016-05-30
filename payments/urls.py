from django.conf.urls import url, patterns

__author__ = "D.Kalpakchi"


urlpatterns = patterns('payments.views',
    url(r'^$', 'payments'),
    url(r'^add/$', 'payments_add'),
    url(r'^template/$', 'payments_template'),
    url(r'^upload_linkpoint/$', 'ajax_upload_archive'),
    url(r'^upload_firstdata/$', 'ajax_add_firstdata')
)