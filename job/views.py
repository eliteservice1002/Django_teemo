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

from .models import Job, JobCandidate, JobFavorite
from .forms import JobForm, CandidateForm
# Create your views here.
# jobs
@method_decorator(login_required, name='dispatch')
class Jobs(TemplateView):
    model = Job
    template_name = "job/jobs.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        context["categories"] = Job.objects.values('category').distinct().order_by()
        context["sel_categories"] = []
        context["favorites"] = JobFavorite.objects.filter(user=self.request.user)
        return context

class JobDetail(TemplateView):
    model = Job
    template_name = "job/job_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = Job.objects.get(pk=self.kwargs.get('pk'))
        context['job'] = job
        context['job_candidates'] = JobCandidate.objects.filter(job_id=self.kwargs.get('pk'))
        return context

@method_decorator(login_required, name='dispatch')
class JobAdd(CreateView):
    model = Job
    form_class = JobForm
    template_name = "job/job_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    def get_success_url(self):
        return reverse('jobs')

@method_decorator(login_required, name='dispatch')
class JobUpdate(UpdateView):
    model = Job
    form_class = JobForm
    template_name = "job/job_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = Job.objects.get(pk=self.kwargs.get('pk'))
        context['job'] = job
        return context
    def get_success_url(self):
        job = Job.objects.get(pk=self.kwargs.get('pk'))
        exist = self.request.POST.get('exist')
        if exist == 'NO':
            job.picture = ''
        job.save()
        return reverse('detail-job', kwargs={'pk': self.kwargs.get('pk')})

def ajax_list_jobs(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    selected_owner = request.POST.get('selected_owner')

    base_query = Job.objects.filter(name__icontains=search_key)

    if selected_category != "":
        base_query = base_query.filter(category__in=selected_category.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))
    
    jobs = base_query.order_by('name')
    for job in jobs:
        job.candidate_count = JobCandidate.objects.filter(job_id=job.id).count()

    paginator = Paginator(jobs, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'job/ajax_job_list.html', {'jobs': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_jobs(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    selected_owner = request.POST.get('selected_owner')

    base_query = Job.objects.filter(name__icontains=search_key)

    if selected_category != "":
        base_query = base_query.filter(category__in=selected_category.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))
    
    jobs = base_query.order_by('name')
    for job in jobs:
        job.candidate_count = JobCandidate.objects.filter(job_id=job.id).count()

    paginator = Paginator(jobs, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'job/ajax_job_grid.html', {'jobs': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_jobs(request):
    checked_contacts = request.POST.get('checked_contacts')
    Job.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class JobsFavorite(TemplateView):
    model = Job
    template_name = "job/jobs.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["categories"] = Job.objects.values('category').distinct().order_by()
        favor = JobFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_users"] = favor.owner.split(',')
        context["sel_categories"] = favor.category.split(',')
        

        context["favorites"] = JobFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_job_favorite(request):
    selected_category = request.POST.get('selected_category')
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')

    count = JobFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = JobFavorite.objects.filter(category=selected_category, owner=selected_owner, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = JobFavorite(name=name, category=selected_category, owner=selected_owner, user=request.user)
            favor.save()

            favorites = JobFavorite.objects.filter(user=request.user)
            return render(request, 'job/ajax_favor_jobs.html', {'favorites': favorites})

def ajax_delete_job_favorite(request):
    del_id = request.POST.get('id')
    JobFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_add_candidates(request):
    if request.method == 'POST':
        add_id = request.POST.get('add_id')
        if str(add_id) == "-1":
            obj = JobCandidate(
                job_id = request.POST.get('job_id'),
                name = request.POST.get('name'),
                description = request.POST.get('description'),
                tag = request.POST.get('tag'),
                picture = request.FILES.get('picture'),
                pdf = request.FILES.get('pdf')
            )
            obj.save()
        else:
            obj = JobCandidate.objects.get(id=add_id)
            obj.name = request.POST.get('name')
            obj.job_id = request.POST.get('job_id')
            obj.description = request.POST.get('description')
            obj.tag = request.POST.get('tag')
            if request.FILES.get('picture') is not None:
                obj.picture = request.FILES.get('picture')
            if request.FILES.get('pdf') is not None:
                obj.pdf = request.FILES.get('pdf')

            exist = request.POST.get('exist')
            exist_pdf = request.POST.get('exist_pdf')
            if exist == 'NO':
                obj.picture = ''
            if exist_pdf == 'NO':
                obj.pdf = ''
            obj.save()

    return JsonResponse({'status': 'ok'})

def ajax_grid_candidates(request):
    job_id = request.POST.get('job_id')
    
    items = JobCandidate.objects.filter(job_id=job_id).order_by('-tag')
    
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'job/ajax_candidates_grid.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_list_candidates(request):
    job_id = request.POST.get('job_id')
    
    items = JobCandidate.objects.filter(job_id=job_id).order_by('-tag')
    
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'job/ajax_candidates_list.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_candidates(request):
    checked_stocks = request.POST.get('checked_stocks')
    JobCandidate.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})