from django.conf.urls import url, patterns

urlpatterns = patterns('reports_views.views',
                       # report patterns plain urls
                       url(r'^patterns/$', 'patterns'),
                       url(r'^patterns/create/(?P<alias>[a-z_]+)$', 'create_report_pattern'),
                       url(r'^patterns/edit/(?P<pattern_id>[0-9]+|)$', 'edit_report_pattern'),

                       # report patterns ajax urls
                       url(r'^patterns/save$', 'save_report_pattern'),
                       url(r'^patterns/remove&', 'remove_report_pattern'),
                       url(r'^patterns/build&', 'build_report_pattern'),

                       # reports plain urls
                       url(r'^reports/$', 'reports'),
                       url(r'^reports/create/(?P<pattern_id>[0-9]+|)$', 'create_report'),
                       url(r'^reports/show/(?P<report_id>[0-9]+|)$', 'show_report'),
                       url(r'^reports/download/(?P<report_id>[0-9]+|)$', 'download_report'),

                       # reports ajax url
                       url(r'^reports/save$', 'save_report'),
                       url(r'^reports/remove&', 'remove_report'),

                       # report data sources plain urls
                       url(r'^data_sources/$', 'data_sources'),
                       url(r'^data_sources/edit/(?P<alias>[a-z_]+)$', 'data_source_edit'),

                       # report data sources ajax urls
                       url(r'^data_sources/save&', 'data_source_save'),

                       # JASPER REPORTS URL
                       url(r'^jasper/reports/$', 'jasper_reports'),
                       url(r'^jasper/templates/$', 'jasper_templates'),
                       url(r'^jasper/templates/save/$', 'save_jasper_template'),
                       url(r'^jasper/templates/remove/&', 'remove_jasper_template'),
                       url(r'^jasper/templates/edit/(?P<id>[0-9]+|)$', 'jasper_template_edit'),
                       url(r'^jasper/ajax/get_params/$', 'get_jasper_report_params'),
                       url(r'^jasper/ajax/build/$', 'build_jasper_html_report'),
                       url(r'^jasper/download/$', 'download_jasper_report'),
)