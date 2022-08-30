from django.urls import path
from django.conf.urls import url

from .views import Projects

urlpatterns = [
    url(r'^projects/$', Projects.as_view(), name='projects'),
]