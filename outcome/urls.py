from django.urls import path
from django.conf.urls import url

from .views import Outcomes, OutcomeDetail, OutcomesFavorite
from .views import ajax_add_outcome, ajax_list_outcomes, ajax_grid_outcomes, ajax_delete_outcomes
from .views import ajax_add_outcome_favorite, ajax_delete_outcome_favorite
from .views import ajax_add_outcome_item, ajax_delete_outcome_item, ajax_list_outcome_item, ajax_grid_outcome_item

from .views import Pickings, PickingDetail, ajax_get_pickings, ajax_finish_picking
urlpatterns = [
    url(r'^outcomes/$', Outcomes.as_view(), name='outcomes'),
    url(r'^outcomes/favorite/(?P<pk>\d+)$', OutcomesFavorite.as_view(), name='favor-outcome'),
    url(r'^ajax-add-outcome/$', ajax_add_outcome, name='ajax-add-outcome'),
    url(r'^detail-outcome/(?P<pk>\d+)/$', OutcomeDetail.as_view(), name='detail-outcome'),

    url(r'^ajax-list-outcomes/$', ajax_list_outcomes, name='ajax-list-outcomes'),
    url(r'^ajax-grid-outcomes/$', ajax_grid_outcomes, name='ajax-grid-outcomes'),
    url(r'^ajax-delete-outcomes/$', ajax_delete_outcomes, name='ajax-delete-outcomes'),

    url(r'^ajax-add-outcome-favorite/$', ajax_add_outcome_favorite, name='ajax-add-outcome-favorite'),
    url(r'^ajax-delete-outcome-favorite/$', ajax_delete_outcome_favorite, name='ajax-delete-outcome-favorite'),

    url(r'^ajax-add-outcome-item/$', ajax_add_outcome_item, name='ajax-add-outcome-item'),
    url(r'^ajax-delete-outcome-item/$', ajax_delete_outcome_item, name='ajax-delete-outcome-item'),
    url(r'^ajax-list-outcome-item/$', ajax_list_outcome_item, name='ajax-list-outcome-item'),
    url(r'^ajax-grid-outcome-item/$', ajax_grid_outcome_item, name='ajax-grid-outcome-item'),
    
    ########## page for picker ###########
    url(r'^pickings/$', Pickings.as_view(), name='pickings'),
    url(r'^ajax-get-pickings/$', ajax_get_pickings, name='ajax-get-pickings'),
    url(r'^detail-picking/(?P<pk>\d+)/$', PickingDetail.as_view(), name='detail-picking'),
    url(r'^ajax-finish-picking/$', ajax_finish_picking, name='ajax-finish-picking'),
]