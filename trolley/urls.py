from django.urls import path
from django.conf.urls import url

from .views import Trolleys, TrolleyDetail, TrolleysFavorite
from .views import ajax_add_trolley, ajax_list_trolleys, ajax_grid_trolleys, ajax_delete_trolleys
from .views import ajax_add_trolley_favorite, ajax_delete_trolley_favorite
from .views import TrolleyOrderItemAdd, TrolleyOrderItemUpdate, ajax_add_trolley_item, ajax_delete_trolley_item, ajax_list_trolley_item, ajax_grid_trolley_item
from .views import ajax_duplicate_trolley_item, ajax_get_trolley_item_id

from .views import ajax_add_accessories_item, ajax_delete_accessories_item, ajax_list_accessories_item, ajax_grid_accessories_item

from .views import ajax_get_stock_image
from .views import ajax_finish_trolley_item, ajax_delete_final_photo

urlpatterns = [
    url(r'^trolleys/$', Trolleys.as_view(), name='trolleys'),
    url(r'^trolleys/favorite/(?P<pk>\d+)$', TrolleysFavorite.as_view(), name='favor-trolley'),
    url(r'^ajax-add-trolley/$', ajax_add_trolley, name='ajax-add-trolley'),
    url(r'^detail-trolley/(?P<pk>\d+)/$', TrolleyDetail.as_view(), name='detail-trolley'),

    url(r'^ajax-list-trolleys/$', ajax_list_trolleys, name='ajax-list-trolleys'),
    url(r'^ajax-grid-trolleys/$', ajax_grid_trolleys, name='ajax-grid-trolleys'),
    url(r'^ajax-delete-trolleys/$', ajax_delete_trolleys, name='ajax-delete-trolleys'),

    url(r'^ajax-add-trolley-favorite/$', ajax_add_trolley_favorite, name='ajax-add-trolley-favorite'),
    url(r'^ajax-delete-trolley-favorite/$', ajax_delete_trolley_favorite, name='ajax-delete-trolley-favorite'),

    
    url(r'^add-trolley-item/(?P<pk>\d+)/$', TrolleyOrderItemAdd.as_view(), name='add-trolley-item'),
    url(r'^detail-trolley-item/(?P<pk>\d+)/$', TrolleyOrderItemUpdate.as_view(), name='detail-trolley-item'),
    url(r'^ajax-get-stock-image', ajax_get_stock_image, name='ajax-get-stock-image'),

    url(r'^ajax-add-trolley-item/$', ajax_add_trolley_item, name='ajax-add-trolley-item'),
    url(r'^ajax-duplicate-trolley-item/$', ajax_duplicate_trolley_item, name='ajax-duplicate-trolley-item'),
    url(r'^ajax-delete-trolley-item/$', ajax_delete_trolley_item, name='ajax-delete-trolley-item'),
    url(r'^ajax-list-trolley-item/$', ajax_list_trolley_item, name='ajax-list-trolley-item'),
    url(r'^ajax-grid-trolley-item/$', ajax_grid_trolley_item, name='ajax-grid-trolley-item'),

    url(r'^ajax-get-trolley-item-id/$', ajax_get_trolley_item_id, name='ajax-get-trolley-item-id'),
    
    url(r'^ajax-add-accessories-item/$', ajax_add_accessories_item, name='ajax-add-accessories-item'),
    url(r'^ajax-delete-accessories-item/$', ajax_delete_accessories_item, name='ajax-delete-accessories-item'),
    url(r'^ajax-list-accessories-item/$', ajax_list_accessories_item, name='ajax-list-accessories-item'),
    url(r'^ajax-grid-accessories-item/$', ajax_grid_accessories_item, name='ajax-grid-accessories-item'),
    
    url(r'^ajax-finish-trolley-item/$', ajax_finish_trolley_item, name='ajax-finish-trolley-item'),
    url(r'^ajax-delete-final-photo/$', ajax_delete_final_photo, name='ajax-delete-final-photo'),
]