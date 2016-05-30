from django.conf.urls import url, patterns

urlpatterns = patterns('rental_fleets.views',
    url(r'^$', 'index'),
    url(r'^ajax_get_tariff_plans/$', 'ajax_get_tariff_plans'),
    url(r'^search_by_upc/$', 'upc_search'),
    url(r'^disks/$', 'disks'),
    url(r'^disks/(?P<disk_rf_id>\S+)/reassign_upc/(?P<upc>\d+)/$', 'reassign_disk_upc'),
    url(r'^disks/add/$', 'add_disk'),
    url(r'^disks/out/$', 'disks_out'),
    url(r'^json_disks_out/$', 'json_disks_out'),
    url(r'^disks/(?P<disk_rf_id>\S+)/$', 'show_disk'),
    url(r'^disks/$', 'show_disk'),
    url(r'^json_disks/$', 'json_disks'),

    url(r'^upcs/(?P<upc>\d+)/priceplan/add$', 'add_upc_price_plan'),
    url(r'^upcs/(?P<upc>\d+)/priceplan$', 'check_upc_price_plan'),
    url(r'^upcs/(?P<upc>\d+)/$', 'show_upc'),
    url(r'^upcs/$', 'show_upc'),
    url(r'^upc_detailed/$', 'upc_detailed'),

    # For focus and company
    url(r'^(?P<company_id>\d+)/view/$', 'view_rental_fleets'),
)