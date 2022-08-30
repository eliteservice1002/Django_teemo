from django.urls import path
from django.conf.urls import url

from .views import Adjusts, AdjustsFavorite
from .views import ajax_add_adjust, ajax_list_adjusts, ajax_grid_adjusts, ajax_delete_adjusts
from .views import ajax_add_adjust_favorite, ajax_delete_adjust_favorite, ajax_odoo_get_adjust

from .views import ajax_get_current_quantity, ajax_adjust_stock
urlpatterns = [
    url(r'^adjusts/$', Adjusts.as_view(), name='adjusts'),
    url(r'^adjusts/favorite/(?P<pk>\d+)$', AdjustsFavorite.as_view(), name='favor-adjust'),
    url(r'^ajax-add-adjust/$', ajax_add_adjust, name='ajax-add-adjust'),
    
    url(r'^ajax-list-adjusts/$', ajax_list_adjusts, name='ajax-list-adjusts'),
    url(r'^ajax-grid-adjusts/$', ajax_grid_adjusts, name='ajax-grid-adjusts'),
    url(r'^ajax-delete-adjusts/$', ajax_delete_adjusts, name='ajax-delete-adjusts'),

    url(r'^ajax-add-adjust-favorite/$', ajax_add_adjust_favorite, name='ajax-add-adjust-favorite'),
    url(r'^ajax-delete-adjust-favorite/$', ajax_delete_adjust_favorite, name='ajax-delete-adjust-favorite'),
    
    url(r'^ajax-get-current-quantity/$', ajax_get_current_quantity, name='ajax-get-current-quantity'),
    url(r'^ajax-adjust-stock/$', ajax_adjust_stock, name='ajax-adjust-stock'),
    url(r'^ajax-receive-adjust/$', ajax_odoo_get_adjust, name='ajax-receive-adjust'),
]