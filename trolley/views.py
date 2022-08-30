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
from backend.models import WallType, Castor, Color, DrawerColor, Strip, Lock

from .models import TrolleyOrder, TrolleyOrderItem, TrolleyOrderFavorite, AccesoriesItem, FinalPhotos

from datetime import datetime
from datetime import date

# trolleys
@method_decorator(login_required, name='dispatch')
class Trolleys(TemplateView):
    model = TrolleyOrder
    template_name = "trolley/trolleys.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        context["clients"] = Client.objects.all()
        context["sel_clients"] = []

        today = date.today()
        start_date = TrolleyOrder.objects.all().aggregate(Min('order_date'))["order_date__min"]
        context["start_date"] = today if start_date == None else start_date 
        end_date = TrolleyOrder.objects.all().aggregate(Max('order_date'))["order_date__max"]
        context["end_date"] = today if end_date == None else end_date

        context["favorites"] = TrolleyOrderFavorite.objects.filter(user=self.request.user)
        return context

class TrolleyDetail(TemplateView):
    model = TrolleyOrder
    template_name = "trolley/trolley_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trolley = TrolleyOrder.objects.get(pk=self.kwargs.get('pk'))
        trolley.sum_weight = TrolleyOrderItem.objects.filter(trolley_id=self.kwargs.get('pk')).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
        trolley.cube = TrolleyOrderItem.objects.filter(trolley_id=self.kwargs.get('pk')).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']

        context['trolley'] = trolley
        context["clients"] = Client.objects.all()
        context["stocks"] = Stock.objects.exclude(b_group=2)
        
        return context

def ajax_add_trolley(request):
    name = request.POST.get('name')
    order_date = request.POST.get('date')
    description = request.POST.get('description')
    client_id = request.POST.get('client')
    add_id = request.POST.get('add_id')
    
    if str(add_id) == "-1": 
        count = TrolleyOrder.objects.filter(name=name, order_date=order_date).count()
        if count != 0:
            return JsonResponse({'err_code': '1'})
        else:
            obj = TrolleyOrder(name=name, description=description, client_id=client_id, order_date=order_date, user=request.user)
            obj.save()
            return JsonResponse({'err_code': '2', 'trolley_id': obj.id})
    else:
        obj = TrolleyOrder.objects.get(id=add_id)
        obj.name = name
        obj.client_id = client_id
        obj.order_date = order_date
        obj.description = description
        obj.save()
        return JsonResponse({'err_code': '2', 'trolley_id': obj.id})

def ajax_list_trolleys(request):
    search_key = request.POST.get('search_key')
    selected_client = request.POST.get('selected_client')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = TrolleyOrder.objects.filter(name__icontains=search_key).filter(order_date__range=[start_date, end_date])

    if selected_client != "":
        base_query = base_query.filter(client__in=selected_client.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))
    
    trolleys = base_query.order_by('-order_date')
    
    paginator = Paginator(trolleys, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    for item in page_obj:
        temp = TrolleyOrderItem.objects.filter(trolley_id=item.id).filter(finished=False).count()
        temp_all = TrolleyOrderItem.objects.filter(trolley_id=item.id).count()
        if temp == 0 and temp_all != 0:
            item.finished = True
        else:
            item.finished = False

    return render(request, 'trolley/ajax_trolley_list.html', {'trolleys': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_trolleys(request):
    search_key = request.POST.get('search_key')
    selected_client = request.POST.get('selected_client')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = TrolleyOrder.objects.filter(name__icontains=search_key).filter(order_date__range=[start_date, end_date])

    if selected_client != "":
        base_query = base_query.filter(client__in=selected_client.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))

    trolleys = base_query.order_by('-order_date')
    paginator = Paginator(trolleys, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)
    
    for item in page_obj:
        temp = TrolleyOrderItem.objects.filter(trolley_id=item.id).filter(finished=False).count()
        temp_all = TrolleyOrderItem.objects.filter(trolley_id=item.id).count()
        if temp == 0 and temp_all != 0:
            item.finished = True
        else:
            item.finished = False

    return render(request, 'trolley/ajax_trolley_grid.html', {'trolleys': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_trolleys(request):
    checked_contacts = request.POST.get('checked_contacts')
    TrolleyOrder.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class TrolleysFavorite(TemplateView):
    model = TrolleyOrder
    template_name = "trolley/trolleys.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["clients"] = Client.objects.all()
        favor = TrolleyOrderFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_users"] = favor.owner.split(',')
        context["sel_clients"] = favor.client.split(',')
        context["start_date"] = favor.start_date
        context["end_date"] = favor.end_date

        context["favorites"] = TrolleyOrderFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_trolley_favorite(request):
    selected_client = request.POST.get('selected_client')
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    count = TrolleyOrderFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = TrolleyOrderFavorite.objects.filter(client=selected_client, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = TrolleyOrderFavorite(name=name, client=selected_client, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user)
            favor.save()

            favorites = TrolleyOrderFavorite.objects.filter(user=request.user)
            return render(request, 'trolley/ajax_favor_trolleys.html', {'favorites': favorites})

def ajax_delete_trolley_favorite(request):
    del_id = request.POST.get('id')
    TrolleyOrderFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

class TrolleyOrderItemAdd(TemplateView):
    model = TrolleyOrderItem
    template_name = "trolley/trolley_item_add.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trolley = TrolleyOrder.objects.get(pk=self.kwargs.get('pk'))
        
        context['trolley'] = trolley
        context["wallstype"] = WallType.objects.exclude(b_deleted=True)
        context["castors"] = Castor.objects.exclude(b_deleted=True)
        context["colors"] = Color.objects.exclude(b_deleted=True)
        context["drawer_colors"] = DrawerColor.objects.exclude(b_deleted=True)
        context["strips"] = Strip.objects.exclude(b_deleted=True)
        context["locks"] = Lock.objects.exclude(b_deleted=True)
        context["stocks"] = Stock.objects.exclude(b_group=2)
        
        return context

class TrolleyOrderItemUpdate(TemplateView):
    model = TrolleyOrderItem
    template_name = "trolley/trolley_item_add.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trolley_item = TrolleyOrderItem.objects.get(pk=self.kwargs.get('pk'))
        trolley_item.photos = FinalPhotos.objects.filter(trolley_item_id=trolley_item.id)
        trolley_item.accesories = AccesoriesItem.objects.filter(trolley_item_id=trolley_item.id)

        temp_pdf = AccesoriesItem.objects.filter(trolley_item_id=trolley_item.id).values('stock').order_by('stock').annotate(quantity=Sum('quantity'))
        for temp in temp_pdf:
            temp["stock_item"] = Stock.objects.get(id=temp["stock"])
        
        trolley_item.accesories_pdf = temp_pdf

        context["trolley_item"] = trolley_item
        context['trolley'] = TrolleyOrder.objects.get(id=trolley_item.trolley_id)
        context["wallstype"] = WallType.objects.exclude(b_deleted=True)
        context["castors"] = Castor.objects.exclude(b_deleted=True)
        context["colors"] = Color.objects.exclude(b_deleted=True)
        context["drawer_colors"] = DrawerColor.objects.exclude(b_deleted=True)
        context["strips"] = Strip.objects.exclude(b_deleted=True)
        context["locks"] = Lock.objects.exclude(b_deleted=True)
        context["stocks"] = Stock.objects.exclude(b_group=2)
        context["trolley_count"] = TrolleyOrderItem.objects.filter(trolley_id=trolley_item.trolley_id).count()
        return context
def ajax_get_stock_image(request):
    stock_id = request.POST.get('stock_id')
    stock = Stock.objects.get(id=stock_id)
    return render(request, 'trolley/ajax_get_trolley_image.html', {'stock': stock})

def ajax_add_trolley_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if str(item_id) == "-1":
            trolley_id = request.POST.get('trolley_order_id')
            count = TrolleyOrderItem.objects.filter(trolley_id=trolley_id).count()

            obj = TrolleyOrderItem(
                position= count+1,
                trolley_id = trolley_id,
                stock_id = request.POST.get('stock_id'),
                order_quantity = request.POST.get('quantity'),
                wall_type_id = request.POST.get('wall_type_id'),
                castor_id = request.POST.get('castor_id'),
                color_side_id = request.POST.get('color_side_id'),
                color_drawer_id = request.POST.get('color_drawer_id'),
                strip_id = request.POST.get('strip_id'),
                lock_id = request.POST.get('lock_id'),
                manu_workers = request.POST.get('manu_workers'),
                clean_worker = request.POST.get('clean_worker'),
                check_worker = request.POST.get('check_worker'),
                configuration = request.POST.get('configuration')
            )
            obj.save()
        else:
            obj = TrolleyOrderItem.objects.get(id=item_id)
            obj.stock_id = request.POST.get('stock_id')
            obj.order_quantity = request.POST.get('quantity')
            obj.wall_type_id = request.POST.get('wall_type_id')
            obj.castor_id = request.POST.get('castor_id')
            obj.color_side_id = request.POST.get('color_side_id')
            obj.color_drawer_id = request.POST.get('color_drawer_id')
            obj.strip_id = request.POST.get('strip_id')
            obj.lock_id = request.POST.get('lock_id')
            obj.manu_workers = request.POST.get('manu_workers')
            obj.clean_worker = request.POST.get('clean_worker')
            obj.check_worker = request.POST.get('check_worker')
            obj.configuration = request.POST.get('configuration')
            obj.save()

    return JsonResponse({'status': 'ok', 'trolley_item_id': obj.id, 'trolley_position': obj.position})
def ajax_duplicate_trolley_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        duplicate_time = request.POST.get('duplicate_time')
        trolley_id = request.POST.get('trolley_order_id')
        count = TrolleyOrderItem.objects.filter(trolley_id=trolley_id).count()
        count = count + 1

        dup_obj = TrolleyOrderItem.objects.get(id=item_id)
        for i in range(int(duplicate_time)):
            obj = TrolleyOrderItem(
                position= count+i,
                trolley_id = dup_obj.trolley_id,
                stock_id = dup_obj.stock_id,
                order_quantity = dup_obj.order_quantity,
                wall_type_id = dup_obj.wall_type_id,
                castor_id = dup_obj.castor_id,
                color_side_id = dup_obj.color_side_id,
                color_drawer_id = dup_obj.color_drawer_id,
                strip_id = dup_obj.strip_id,
                lock_id = dup_obj.lock_id,
                manu_workers = dup_obj.manu_workers,
                clean_worker = dup_obj.clean_worker,
                check_worker = dup_obj.check_worker,
                configuration = dup_obj.configuration,
            )
            obj.save()
            access = AccesoriesItem.objects.filter(trolley_item_id=item_id)
            for temp in access:
                acess_obj = AccesoriesItem(
                    trolley_item_id = obj.id,
                    stock_id = temp.stock_id,
                    description = temp.description,
                    direction = temp.direction,
                    packaging = temp.packaging,
                    quantity = temp.quantity,
                )
                acess_obj.save()

    return JsonResponse({'status': 'ok'})
def ajax_get_trolley_item_id(request):
    if request.method == 'POST':
        current_position = request.POST.get('trolley_position')
        trolley_id = request.POST.get('trolley_order_id')
        action_type = request.POST.get('action_type')
        if action_type == "NEXT":
            action_postion = int(current_position) + 1
        else:
            action_postion = int(current_position) - 1

        obj = TrolleyOrderItem.objects.get(position=action_postion, trolley_id=trolley_id)

    return JsonResponse({'status': 'ok', 'trolley_item_id': obj.id})
def ajax_grid_trolley_item(request):
    trolley_id = request.POST.get('trolley_id')
    
    sum_weight = TrolleyOrderItem.objects.filter(trolley_id=trolley_id).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
    cube = TrolleyOrderItem.objects.filter(trolley_id=trolley_id).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']
    items = TrolleyOrderItem.objects.filter(trolley_id=trolley_id).order_by('id')
    
    paginator = Paginator(items, 16)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'trolley/ajax_trolley_item_grid.html', {'items': page_obj, 'sum_weight':sum_weight, 'cube':cube, 'page_obj': page_obj, 'paginator': paginator})

def ajax_list_trolley_item(request):
    trolley_id = request.POST.get('trolley_id')
    
    sum_weight = TrolleyOrderItem.objects.filter(trolley_id=trolley_id).annotate(tweight=F('stock__weight')*F('order_quantity')).aggregate(Sum('tweight'))['tweight__sum']
    cube = TrolleyOrderItem.objects.filter(trolley_id=trolley_id).annotate(cube=F('stock__width') * F('stock__height')* F('stock__depth')*F('order_quantity')).aggregate(Sum('cube'))['cube__sum']
    items = TrolleyOrderItem.objects.filter(trolley_id=trolley_id).order_by('id')

    paginator = Paginator(items, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'trolley/ajax_trolley_item_list.html', {'items': page_obj, 'sum_weight':sum_weight, 'cube':cube, 'page_obj': page_obj, 'paginator': paginator})
def ajax_delete_trolley_item(request):
    checked_stocks = request.POST.get('checked_stocks')
    trolley_id = request.POST.get('trolley_id')

    TrolleyOrderItem.objects.filter(id__in=checked_stocks.split(',')).delete()

    trolleyItems = TrolleyOrderItem.objects.filter(trolley_id=trolley_id)
    count = 1
    for item in trolleyItems:
        item.position = count
        item.save()
        count = count + 1
    
    return JsonResponse({'status': 'ok'})

def ajax_finish_trolley_item(request):
    files = request.FILES.getlist('files[]')
    trolley_item_id = request.POST.get('trolley_item_id')
    finished_time = request.POST.get('finished_time')
    check_description = request.POST.get('check_description')
    
    obj = TrolleyOrderItem.objects.get(id=trolley_item_id)
    obj.finished_time = finished_time
    obj.check_description = check_description
    obj.finished = True
    obj.save()

    for file in files:
        obj = FinalPhotos(
            trolley_item_id = trolley_item_id,
            picture = file
            )
        obj.save()
    return JsonResponse({'status': 'ok'})

def ajax_delete_final_photo(request):
    obj = FinalPhotos.objects.get(id=request.POST.get('item_id'))
    obj.delete()
    return JsonResponse({'status': 'ok'})

def ajax_add_accessories_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('add_id')
        if str(item_id) == "-1":
            obj = AccesoriesItem(
                trolley_item_id = request.POST.get('trolley_item_id'),
                stock_id = request.POST.get('stock_id'),
                description = request.POST.get('description'),
                direction = request.POST.get('direction'),
                quantity = request.POST.get('quantity'),
                packaging = request.POST.get('packaging'),
            )
            obj.save()
        else:
            obj = AccesoriesItem.objects.get(id=item_id)
            obj.trolley_item_id = request.POST.get('trolley_item_id')
            obj.stock_id = request.POST.get('stock_id')
            obj.description = request.POST.get('description')
            obj.direction = request.POST.get('direction')
            obj.quantity = request.POST.get('quantity')
            obj.packaging = request.POST.get('packaging')
            obj.save()

    return JsonResponse({'status': 'ok'})

def ajax_grid_accessories_item(request):
    trolley_item_id = request.POST.get('trolley_item_id')
    
    items = AccesoriesItem.objects.filter(trolley_item_id=trolley_item_id).order_by('id')
    
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'trolley/ajax_accessories_item_grid.html', {'items': page_obj,  'page_obj': page_obj, 'paginator': paginator})

def ajax_list_accessories_item(request):
    trolley_item_id = request.POST.get('trolley_item_id')
    
    items = AccesoriesItem.objects.filter(trolley_item_id=trolley_item_id).order_by('id')

    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'trolley/ajax_accessories_item_list.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})
def ajax_delete_accessories_item(request):
    checked_stocks = request.POST.get('checked_stocks')
    AccesoriesItem.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})
