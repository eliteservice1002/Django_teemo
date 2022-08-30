from django.urls import path
from django.conf.urls import url

from .views import TimeSheets, TimeSheetDetail, TimeSheetsFavorite
from .views import ajax_add_timesheet, ajax_list_timesheets, ajax_grid_timesheets, ajax_delete_timesheets
from .views import ajax_add_timesheet_favorite, ajax_delete_timesheet_favorite
from .views import ajax_add_timesheet_item, ajax_delete_timesheet_item, ajax_list_timesheet_item, ajax_grid_timesheet_item


urlpatterns = [
    url(r'^timesheets/$', TimeSheets.as_view(), name='timesheets'),
    url(r'^timesheets/favorite/(?P<pk>\d+)$', TimeSheetsFavorite.as_view(), name='favor-timesheet'),
    url(r'^ajax-add-timesheet/$', ajax_add_timesheet, name='ajax-add-timesheet'),
    url(r'^detail-timesheet/(?P<pk>\d+)/$', TimeSheetDetail.as_view(), name='detail-timesheet'),

    url(r'^ajax-list-timesheets/$', ajax_list_timesheets, name='ajax-list-timesheets'),
    url(r'^ajax-grid-timesheets/$', ajax_grid_timesheets, name='ajax-grid-timesheets'),
    url(r'^ajax-delete-timesheets/$', ajax_delete_timesheets, name='ajax-delete-timesheets'),

    url(r'^ajax-add-timesheet-favorite/$', ajax_add_timesheet_favorite, name='ajax-add-timesheet-favorite'),
    url(r'^ajax-delete-timesheet-favorite/$', ajax_delete_timesheet_favorite, name='ajax-delete-timesheet-favorite'),

    url(r'^ajax-add-timesheet-item/$', ajax_add_timesheet_item, name='ajax-add-timesheet-item'),
    url(r'^ajax-delete-timesheet-item/$', ajax_delete_timesheet_item, name='ajax-delete-timesheet-item'),
    url(r'^ajax-list-timesheet-item/$', ajax_list_timesheet_item, name='ajax-list-timesheet-item'),
    url(r'^ajax-grid-timesheet-item/$', ajax_grid_timesheet_item, name='ajax-grid-timesheet-item'),
]