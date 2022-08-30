from django.urls import path
from django.conf.urls import url

from .views import Purchases, PurchaseDetail, PurchasesFavorite
from .views import ajax_list_purchases, ajax_grid_purchases, ajax_delete_purchases
from .views import ajax_add_purchase_favorite, ajax_delete_purchase_favorite
from .views import ajax_add_order_item, ajax_delete_order_item, ajax_list_order_item, ajax_grid_order_item
from .views import ajax_add_purchase, ajax_update_income_order_item, ajax_update_valid_order_item

from .views import Transports, TransportAdd, TransportDetail, TransportUpdate, TransportsFavorite
from .views import ajax_transport_new_detail
from .views import ajax_list_transports, ajax_grid_transports, ajax_delete_transports
from .views import ajax_add_departure_item, ajax_delete_departure_item, ajax_list_departure_item, ajax_grid_departure_item
from .views import ajax_add_transport_favorite, ajax_delete_transport_favorite

from .views import Brokens, BrokenDetail, BrokensFavorite
from .views import ajax_list_brokens, ajax_grid_brokens, ajax_list_broken_detail
from .views import ajax_add_broken_favorite, ajax_delete_broken_favorite

from .views import RefundsHistory, RefundsFavorite
from .views import ajax_list_refunds, ajax_grid_refunds
from .views import ajax_get_brokens_from_date, ajax_add_broken_refund
from .views import ajax_add_refund_favorite, ajax_delete_refund_favorite
urlpatterns = [
    url(r'^purchases/$', Purchases.as_view(), name='purchases'),
    url(r'^purchases/favorite/(?P<pk>\d+)$', PurchasesFavorite.as_view(), name='favor-purchase'),
    url(r'^ajax-add-purchase/$', ajax_add_purchase, name='ajax-add-purchase'),
    url(r'^detail-purchase/(?P<pk>\d+)/$', PurchaseDetail.as_view(), name='detail-purchase'),
    url(r'^ajax-list-purchases/$', ajax_list_purchases, name='ajax-list-purchases'),
    url(r'^ajax-grid-purchases/$', ajax_grid_purchases, name='ajax-grid-purchases'),
    url(r'^ajax-delete-purchases/$', ajax_delete_purchases, name='ajax-delete-purchases'),

    url(r'^ajax-add-purchase-favorite/$', ajax_add_purchase_favorite, name='ajax-add-purchase-favorite'),
    url(r'^ajax-delete-purchase-favorite/$', ajax_delete_purchase_favorite, name='ajax-delete-purchase-favorite'),

    url(r'^ajax-add-order-item/$', ajax_add_order_item, name='ajax-add-order-item'),
    url(r'^ajax-delete-order-item/$', ajax_delete_order_item, name='ajax-delete-order-item'),
    url(r'^ajax-list-order-item/$', ajax_list_order_item, name='ajax-list-order-item'),
    url(r'^ajax-grid-order-item/$', ajax_grid_order_item, name='ajax-grid-order-item'),

    url(r'^ajax-update-income-order-item/$', ajax_update_income_order_item, name='ajax-update-income-order-item'),
    url(r'^ajax-update-valid-order-item/$', ajax_update_valid_order_item, name='ajax-update-valid-order-item'),

    # transport
    url(r'^transports/$', Transports.as_view(), name='transports'),
    url(r'^transports/favorite/(?P<pk>\d+)$', TransportsFavorite.as_view(), name='favor-transport'),
    url(r'^new-transport/$', TransportAdd.as_view(), name='new-transport'),
    url(r'^update-transport/(?P<pk>\d+)/$', TransportUpdate.as_view(), name='update-transport'),
    url(r'^ajax-transport-new-detail/$', ajax_transport_new_detail, name='ajax-transport-new-detail'),
    url(r'^detail-transport/(?P<pk>\d+)/$', TransportDetail.as_view(), name='detail-transport'),

    url(r'^ajax-add-transport-favorite/$', ajax_add_transport_favorite, name='ajax-add-transport-favorite'),
    url(r'^ajax-delete-transport-favorite/$', ajax_delete_transport_favorite, name='ajax-delete-transport-favorite'),

    url(r'^ajax-list-transports/$', ajax_list_transports, name='ajax-list-transports'),
    url(r'^ajax-grid-transports/$', ajax_grid_transports, name='ajax-grid-transports'),
    url(r'^ajax-delete-transports/$', ajax_delete_transports, name='ajax-delete-transports'),

    url(r'^ajax-add-departure-item/$', ajax_add_departure_item, name='ajax-add-departure-item'),
    url(r'^ajax-delete-departure-item/$', ajax_delete_departure_item, name='ajax-delete-departure-item'),
    url(r'^ajax-list-departure-item/$', ajax_list_departure_item, name='ajax-list-departure-item'),
    url(r'^ajax-grid-departure-item/$', ajax_grid_departure_item, name='ajax-grid-departure-item'),

    # broken
    url(r'^brokens/$', Brokens.as_view(), name='brokens'),
    url(r'^ajax-list-brokens/$', ajax_list_brokens, name='ajax-list-brokens'),
    url(r'^ajax-grid-brokens/$', ajax_grid_brokens, name='ajax-grid-brokens'),

    url(r'^detail-broken/(?P<supplier_id>\d+)/(?P<stock_id>\d+)/$', BrokenDetail.as_view(), name='detail-broken'),
    url(r'^ajax-list-broken-detail/$', ajax_list_broken_detail, name='ajax-list-broken-detail'),

    url(r'^brokens/favorite/(?P<pk>\d+)$', BrokensFavorite.as_view(), name='favor-broken'),
    url(r'^ajax-add-broken-favorite/$', ajax_add_broken_favorite, name='ajax-add-broken-favorite'),
    url(r'^ajax-delete-broken-favorite/$', ajax_delete_broken_favorite, name='ajax-delete-broken-favorite'),

    url(r'^ajax-get-brokens-from-date/$', ajax_get_brokens_from_date, name='ajax-get-brokens-from-date'),

    # refund
    url(r'^broken-history/$', RefundsHistory.as_view(), name='broken-history'),
    url(r'^ajax-list-refunds/$', ajax_list_refunds, name='ajax-list-refunds'),
    url(r'^ajax-grid-refunds/$', ajax_grid_refunds, name='ajax-grid-refunds'),
    url(r'^ajax-add-broken-refund/$', ajax_add_broken_refund, name='ajax-add-broken-refund'),

    url(r'^broken-history/favorite/(?P<pk>\d+)$', RefundsFavorite.as_view(), name='favor-refund'),
    url(r'^ajax-add-refund-favorite/$', ajax_add_refund_favorite, name='ajax-add-refund-favorite'),
    url(r'^ajax-delete-refund-favorite/$', ajax_delete_refund_favorite, name='ajax-delete-refund-favorite'),
]