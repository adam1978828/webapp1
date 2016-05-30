from django.conf.urls import url, patterns
from django.conf import settings


__author__ = 'D.Kalpakchi'


urlpatterns = patterns(
    'sites.views',
    url(r'^$', 'index'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),

    url(r'^signup/step1/$', 'signup_step1'),
    url(r'^ajax_signup/step1/$', 'ajax_signup_step1'),
    url(r'^signup/step2/confirmation/(.*)/$', 'signup_step2_confirm'),
    url(r'^signup/step2/default$', 'signup_step2_default'),
    url(r'^signup/step3/$', 'signup_step3'),

    url(r'^password/restore/default/$', 'password_restore_default'),
    url(r'^password/restore/confirmation/(.*)/$', 'password_restore_confirm'),
    url(r'^password/restore/$', 'password_restore'),

    url(r'^register/$', 'register_user'),

    url(r'^movies/$', 'preferred_kiosk_movies'),
    url(r'^movies/(?P<movie_id>\d+)/$', 'movie_details'),
    url(r'^movies/reserve/$', 'add_to_cart'),
    url(r'^movies/search/$', 'movies_search'),
    url(r'^contacts/$', 'contacts'),
    url(r'^kiosks/$', 'company_kiosks'),
    url(r'^kiosks/preferred/$', 'preferred_kiosk'),
    url(r'^kiosks/(?P<kiosk_id>\d+)/$', 'specific_kiosk'),
    url(r'^cart/$', 'cart'),
    url(r'^cart/remove/$', 'remove_from_cart'),
    url(r'^cart/check/$', 'check_cart'),
    url(r'^user/cards/$', 'choose_card'),
    url(r'^user/reservations/add/coupon/$', 'add_coupon'),
    url(r'^user/reservations/specific/$', 'user_reservation'),
    url(r'^user/reservations/$', 'user_reservations'),

    url(r'^personal-data/$', 'personal_data'),
    url(r'^ajax-personal-data/$', 'ajax_personal_data'),

    url(r'^change-password/$', 'change_password'),
    url(r'^ajax-change-password/$', 'ajax_change_password'),

    url(r'^credit-cards/$', 'credit_cards'),
    url(r'^credit-card/add/$', 'add_credit_card'),
    url(r'^credit-card/ajax-add/$', 'ajax_add_credit_card'),
    url(r'^credit-card/remove/(?P<credit_card_id>\S+)/$', 'remove_credit_card'),

    url(r'^signup/$', 'signup'),
    url(r'^ajax-signup/$', 'ajax_signup'),
    url(r'^signup/confirmation/(.*)/$', 'signup_confirm'),
    url(r'^signup/default/$', 'signup_default'),
    url(r'^ajax_signup_confirm/$', 'ajax_signup_confirm'),


)

# media files (images, videos, etc.) for sites
# this is OBLIGATORY setting not for only debug!
urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT})
)
