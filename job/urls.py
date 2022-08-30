from django.urls import path
from django.conf.urls import url

from .views import Jobs, JobAdd, JobDetail, JobUpdate, JobsFavorite
from .views import ajax_list_jobs, ajax_grid_jobs, ajax_delete_jobs
from .views import ajax_add_job_favorite, ajax_delete_job_favorite
from .views import ajax_add_candidates, ajax_delete_candidates, ajax_list_candidates, ajax_grid_candidates


urlpatterns = [
    url(r'^jobs/$', Jobs.as_view(), name='jobs'),
    url(r'^jobs/favorite/(?P<pk>\d+)$', JobsFavorite.as_view(), name='favor-job'),
    url(r'^new-job/$', JobAdd.as_view(), name='new-job'),
    url(r'^update-job/(?P<pk>\d+)/$', JobUpdate.as_view(), name='update-job'),
    url(r'^detail-job/(?P<pk>\d+)/$', JobDetail.as_view(), name='detail-job'),

    url(r'^ajax-list-jobs/$', ajax_list_jobs, name='ajax-list-jobs'),
    url(r'^ajax-grid-jobs/$', ajax_grid_jobs, name='ajax-grid-jobs'),
    url(r'^ajax-delete-jobs/$', ajax_delete_jobs, name='ajax-delete-jobs'),

    url(r'^ajax-add-job-favorite/$', ajax_add_job_favorite, name='ajax-add-job-favorite'),
    url(r'^ajax-delete-job-favorite/$', ajax_delete_job_favorite, name='ajax-delete-job-favorite'),

    url(r'^ajax-add-candidates/$', ajax_add_candidates, name='ajax-add-candidates'),
    url(r'^ajax-delete-candidates/$', ajax_delete_candidates, name='ajax-delete-candidates'),
    url(r'^ajax-list-candidates/$', ajax_list_candidates, name='ajax-list-candidates'),
    url(r'^ajax-grid-candidates/$', ajax_grid_candidates, name='ajax-grid-candidates'),
]