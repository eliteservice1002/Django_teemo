from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, TemplateView
from django.views.generic import FormView, RedirectView, View

from django.db.models import Q
from django.db.models import F
from django.db.models import DurationField, ExpressionWrapper

from django.db.models import Max, Min, Sum
from django.core.paginator import Paginator

from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect

from backend.models import User

from .models import ProjectColumn
# Create your views here.
# projects
@method_decorator(login_required, name='dispatch')
class Projects(TemplateView):
    model = ProjectColumn
    template_name = "job/jobs.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
