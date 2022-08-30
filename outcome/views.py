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

from backend.models import User, Client, Stock

from .models import Outcome, OutcomeItem, OutcomeFavorite

from datetime import datetime
from datetime import date

# outcomes
@method_decorator(login_required, name='dispatch')
class Outcomes(TemplateView):
    model = Outcome
    template_name = "outcome/outcomes.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        context["clients"] = Client.objects.all()
        context["sel_clients"] = []
        today = date.today()
        start_date = Outcome.objects.all().aggregate(Min('order_date'))["order_date__min"]
        context["start_date"] = today if start_date == None else start_date 
        end_date = Outcome.objects.all().aggregate(Max('order_date'))["order_date__max"]
        context["end_date"] = today if end_date == None else end_date

        context["favorites"] = OutcomeFavorite.objects.filter(user=self.request.user)
        return context

class OutcomeDetail(TemplateView):
    model = Outcome
    template_name = "outcome/outcome_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        outcome = Outcome.objects.get(pk=self.kwargs.get('pk'))
        outcome.sum_weight = OutcomeItem.objects.filter(outcome_id=self.kwargs.get('pk')).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
        outcome.cube = OutcomeItem.objects.filter(outcome_id=self.kwargs.get('pk')).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']

        context['outcome'] = outcome
        context["clients"] = Client.objects.all()
        context["stocks"] = Stock.objects.exclude(b_group=2)
        
        return context

def ajax_add_outcome(request):
    name = request.POST.get('name')
    order_date = request.POST.get('date')
    description = request.POST.get('description')
    client_id = request.POST.get('client')
    add_id = request.POST.get('add_id')
    
    if str(add_id) == "-1": 
        count = Outcome.objects.filter(name=name, order_date=order_date).count()
        if count != 0:
            return JsonResponse({'err_code': '1'})
        else:
            obj = Outcome(name=name, description=description, client_id=client_id, order_date=order_date, user=request.user)
            obj.save()
            return JsonResponse({'err_code': '2', 'outcome_id': obj.id})
    else:
        obj = Outcome.objects.get(id=add_id)
        obj.name = name
        obj.client_id = client_id
        obj.order_date = order_date
        obj.description = description
        obj.save()
        return JsonResponse({'err_code': '2', 'outcome_id': obj.id})

def ajax_list_outcomes(request):
    search_key = request.POST.get('search_key')
    selected_client = request.POST.get('selected_client')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = Outcome.objects.filter(name__icontains=search_key).filter(order_date__range=[start_date, end_date])

    if selected_client != "":
        base_query = base_query.filter(client__in=selected_client.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))
    
    outcomes = base_query.order_by('-order_date')
    
    paginator = Paginator(outcomes, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    for item in page_obj:
        item.sum_weight = OutcomeItem.objects.filter(outcome_id=item.id).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
        item.cube = OutcomeItem.objects.filter(outcome_id=item.id).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']

    return render(request, 'outcome/ajax_outcome_list.html', {'outcomes': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_outcomes(request):
    search_key = request.POST.get('search_key')
    selected_client = request.POST.get('selected_client')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = Outcome.objects.filter(name__icontains=search_key).filter(order_date__range=[start_date, end_date])

    if selected_client != "":
        base_query = base_query.filter(client__in=selected_client.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))

    outcomes = base_query.order_by('-order_date')
    paginator = Paginator(outcomes, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)
    for item in page_obj:
        item.sum_weight = OutcomeItem.objects.filter(outcome_id=item.id).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
        item.cube = OutcomeItem.objects.filter(outcome_id=item.id).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']

    return render(request, 'outcome/ajax_outcome_grid.html', {'outcomes': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_outcomes(request):
    checked_contacts = request.POST.get('checked_contacts')
    Outcome.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class OutcomesFavorite(TemplateView):
    model = Outcome
    template_name = "outcome/outcomes.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["clients"] = Client.objects.all()
        favor = OutcomeFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_users"] = favor.owner.split(',')
        context["sel_clients"] = favor.client.split(',')
        context["start_date"] = favor.start_date
        context["end_date"] = favor.end_date

        context["favorites"] = OutcomeFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_outcome_favorite(request):
    selected_client = request.POST.get('selected_client')
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    count = OutcomeFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = OutcomeFavorite.objects.filter(client=selected_client, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = OutcomeFavorite(name=name, client=selected_client, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user)
            favor.save()

            favorites = OutcomeFavorite.objects.filter(user=request.user)
            return render(request, 'outcome/ajax_favor_outcomes.html', {'favorites': favorites})

def ajax_delete_outcome_favorite(request):
    del_id = request.POST.get('id')
    OutcomeFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_add_outcome_item(request):
    if request.method == 'POST':
        add_id = request.POST.get('add_id')
        if str(add_id) == "-1":
            obj = OutcomeItem(
                outcome_id = request.POST.get('outcome_id'),
                stock_id = request.POST.get('stock_id'),
                order_quantity = request.POST.get('quantity'),
            )
            obj.save()
        else:
            obj = OutcomeItem.objects.get(id=add_id)
            obj.stock_id = request.POST.get('stock_id')
            obj.order_quantity = request.POST.get('quantity')
            obj.save()

    return JsonResponse({'status': 'ok'})

def ajax_grid_outcome_item(request):
    outcome_id = request.POST.get('outcome_id')
    
    sum_weight = OutcomeItem.objects.filter(outcome_id=outcome_id).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
    cube = OutcomeItem.objects.filter(outcome_id=outcome_id).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']
    items = OutcomeItem.objects.filter(outcome_id=outcome_id).order_by('id')
    
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'outcome/ajax_outcome_item_grid.html', {'items': page_obj, 'sum_weight':sum_weight, 'cube':cube, 'page_obj': page_obj, 'paginator': paginator})

def ajax_list_outcome_item(request):
    outcome_id = request.POST.get('outcome_id')
    
    sum_weight = OutcomeItem.objects.filter(outcome_id=outcome_id).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
    cube = OutcomeItem.objects.filter(outcome_id=outcome_id).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']
    items = OutcomeItem.objects.filter(outcome_id=outcome_id).order_by('id')

    paginator = Paginator(items, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'outcome/ajax_outcome_item_list.html', {'items': page_obj, 'sum_weight':sum_weight, 'cube':cube, 'page_obj': page_obj, 'paginator': paginator})
def ajax_delete_outcome_item(request):
    checked_stocks = request.POST.get('checked_stocks')
    OutcomeItem.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class Pickings(TemplateView):
    model = Outcome
    template_name = "outcome/pickings.html"
    
def ajax_get_pickings(request):
    sel_date = request.POST.get('sel_date')
    # getting box container size
    boxes = Stock.objects.filter(b_group=2).annotate(cube=F('width')*F('height')*F('depth')).order_by('cube')
    for box in boxes:
        print(box.cube, box.name)

    orders = Outcome.objects.filter(order_date=sel_date)
    for item in orders:
        item.sum_weight = OutcomeItem.objects.filter(outcome_id=item.id).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
        cube = OutcomeItem.objects.filter(outcome_id=item.id).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']
        item.cube = cube

    filtered_ids = orders.values_list('id', flat=True)
    order_items = OutcomeItem.objects.filter(outcome_id__in=filtered_ids).values('stock').annotate(quantity=Sum('order_quantity')).order_by()
    for item in order_items:
        item["stock"] = Stock.objects.get(id=item["stock"])
    
    return render(request, 'outcome/pickings_list.html', {'orders': orders, 'order_items':order_items})

@method_decorator(login_required, name='dispatch')
class PickingDetail(TemplateView):
    model = Outcome
    template_name = "outcome/picking_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        outcome = Outcome.objects.get(pk=self.kwargs.get('pk'))
        outcome.sum_weight = OutcomeItem.objects.filter(outcome_id=self.kwargs.get('pk')).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
        outcome.cube = OutcomeItem.objects.filter(outcome_id=self.kwargs.get('pk')).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']

        order_items = OutcomeItem.objects.filter(outcome_id=outcome.id)
        
        context['outcome'] = outcome
        context['order_items'] = order_items
        
        return context

def ajax_finish_picking(request):
    outcome_id = request.POST.get('outcome_id')
    outcome = Outcome.objects.get(id=outcome_id)
    outcome.finished = True
    outcome.save()
    return HttpResponse('ok')
