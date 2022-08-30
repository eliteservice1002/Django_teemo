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

from backend.models import User, Client, Stock, Task

from .models import TimeSheet, TimeSheetItem, TimeSheetFavorite

from datetime import datetime
from datetime import date
# timesheets
@method_decorator(login_required, name='dispatch')
class TimeSheets(TemplateView):
    model = TimeSheet
    template_name = "timesheet/timesheets.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        today = date.today()
        start_date = TimeSheet.objects.all().aggregate(Min('date'))["date__min"]
        context["start_date"] = today if start_date == None else start_date 
        end_date = TimeSheet.objects.all().aggregate(Max('date'))["date__max"]
        context["end_date"] = today if end_date == None else end_date

        context["favorites"] = TimeSheetFavorite.objects.filter(user=self.request.user)
        return context

class TimeSheetDetail(TemplateView):
    model = TimeSheet
    template_name = "timesheet/timesheet_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timesheet = TimeSheet.objects.get(pk=self.kwargs.get('pk'))
        
        context['timesheet'] = timesheet
        context["users"] = User.objects.all()
        context["stocks"] = Stock.objects.exclude(b_group=2)
        context["tasks"] = Task.objects.exclude(b_deleted=True)
        
        return context

def ajax_add_timesheet(request):
    user_id = request.POST.get('user')
    date = request.POST.get('date')
    add_id = request.POST.get('add_id')
    
    if str(add_id) == "-1": 
        count = TimeSheet.objects.filter(user_id=user_id, date=date).count()
        if count != 0:
            return JsonResponse({'err_code': '1'})
        else:
            obj = TimeSheet(user_id=user_id, date=date)
            obj.save()
            return JsonResponse({'err_code': '2', 'timesheet_id': obj.id})
    else:
        obj = TimeSheet.objects.get(id=add_id)
        obj.user_id = user_id
        obj.date = date
        obj.save()
        return JsonResponse({'err_code': '2', 'timesheet_id': obj.id})

def ajax_list_timesheets(request):
    search_key = request.POST.get('search_key')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = TimeSheet.objects.filter(date__range=[start_date, end_date])

    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))
    
    timesheets = base_query.order_by('-date')
    
    paginator = Paginator(timesheets, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'timesheet/ajax_timesheet_list.html', {'timesheets': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_timesheets(request):
    search_key = request.POST.get('search_key')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = TimeSheet.objects.filter(date__range=[start_date, end_date])

    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))

    timesheets = base_query.order_by('-date')
    paginator = Paginator(timesheets, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'timesheet/ajax_timesheet_grid.html', {'timesheets': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_timesheets(request):
    checked_contacts = request.POST.get('checked_contacts')
    TimeSheet.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class TimeSheetsFavorite(TemplateView):
    model = TimeSheet
    template_name = "timesheet/timesheets.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        favor = TimeSheetFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_users"] = favor.owner.split(',')
        context["start_date"] = favor.start_date
        context["end_date"] = favor.end_date

        context["favorites"] = TimeSheetFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_timesheet_favorite(request):
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    count = TimeSheetFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = TimeSheetFavorite.objects.filter(owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = TimeSheetFavorite(name=name, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user)
            favor.save()

            favorites = TimeSheetFavorite.objects.filter(user=request.user)
            return render(request, 'timesheet/ajax_favor_timesheets.html', {'favorites': favorites})

def ajax_delete_timesheet_favorite(request):
    del_id = request.POST.get('id')
    TimeSheetFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_add_timesheet_item(request):
    if request.method == 'POST':
        add_id = request.POST.get('add_id')
        if str(add_id) == "-1":
            obj = TimeSheetItem(
                timesheet_id = request.POST.get('timesheet_id'),
                stock_id = request.POST.get('stock_id'),
                task_id = request.POST.get('name'),
                start_time = request.POST.get('from_time'),
                end_time = request.POST.get('to_time'),
            )
            obj.save()
        else:
            obj = TimeSheetItem.objects.get(id=add_id)
            obj.stock_id = request.POST.get('stock_id')
            obj.task_id = request.POST.get('name')
            obj.start_time = request.POST.get('from_time')
            obj.end_time = request.POST.get('to_time')
            obj.save()

    return JsonResponse({'status': 'ok'})

def ajax_grid_timesheet_item(request):
    timesheet_id = request.POST.get('timesheet_id')
    
    items = TimeSheetItem.objects.filter(timesheet_id=timesheet_id)

    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'timesheet/ajax_timesheet_item_grid.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_list_timesheet_item(request):
    timesheet_id = request.POST.get('timesheet_id')

    items = TimeSheetItem.objects.filter(timesheet_id=timesheet_id)
    
    paginator = Paginator(items, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'timesheet/ajax_timesheet_item_list.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})
def ajax_delete_timesheet_item(request):
    checked_stocks = request.POST.get('checked_stocks')
    TimeSheetItem.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})
