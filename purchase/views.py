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

from backend.models import User, Contact, Stock

from .models import Purchase, OrderItem, PurchaseFavorite, OrderIncomeValid
from .models import BrokenFavorite
from .models import Transport, DepatureItem, TransportFavorite
from .models import RefundHistory, RefundFavorite
from .forms import TransportForm


from datetime import datetime
from datetime import date
import odoorpc
import pytz
from django.shortcuts import render, redirect
# purchases
@method_decorator(login_required, name='dispatch')
class Purchases(TemplateView):
    model = Purchase
    template_name = "purchase/purchases.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        context["suppliers"] = Contact.objects.all()
        context["sel_suppliers"] = []

        today = date.today()
        start_date = Purchase.objects.all().aggregate(Min('order_date'))["order_date__min"]
        context["start_date"] = today if start_date == None else start_date 
        end_date = Purchase.objects.all().aggregate(Max('order_date'))["order_date__max"]
        context["end_date"] = today if end_date == None else end_date

        context["favorites"] = PurchaseFavorite.objects.filter(user=self.request.user)
        return context

class PurchaseDetail(TemplateView):
    model = Purchase
    template_name = "purchase/purchase_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        purchase = Purchase.objects.get(pk=self.kwargs.get('pk'))
        context['purchase'] = purchase
        context["suppliers"] = Contact.objects.all()
        context["stocks"] = Stock.objects.filter(b_group=False)
        context['purchase_order_item'] = OrderItem.objects.filter(purchase_id=self.kwargs.get('pk'))
        return context
        
def ajax_add_purchase(request):
    name = request.POST.get('name')
    order_date = request.POST.get('date')
    description = request.POST.get('description')
    supplier_id = request.POST.get('supplier')
    add_id = request.POST.get('add_id')
    
    if str(add_id) == "-1": 
        count = Purchase.objects.filter(name=name).count()
        if count != 0:
            return JsonResponse({'err_code': '1'})
        else:
            obj = Purchase(name=name, description=description, supplier_id=supplier_id, order_date=order_date, user=request.user)
            obj.save()
            return JsonResponse({'err_code': '2', 'purchase_id': obj.id})
    else:
        obj = Purchase.objects.get(id=add_id)
        obj.name = name
        obj.supplier_id = supplier_id
        obj.order_date = order_date
        obj.description = description
        obj.save()
        return JsonResponse({'err_code': '2', 'purchase_id': obj.id})

def ajax_list_purchases(request):
    search_key = request.POST.get('search_key')
    selected_supplier = request.POST.get('selected_supplier')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = Purchase.objects.filter(name__icontains=search_key).filter(order_date__range=[start_date, end_date])

    if selected_supplier != "":
        base_query = base_query.filter(supplier__in=selected_supplier.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))
    
    purchases = base_query.order_by('-order_date')
    
    paginator = Paginator(purchases, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'purchase/ajax_purchase_list.html', {'purchases': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_purchases(request):
    search_key = request.POST.get('search_key')
    selected_supplier = request.POST.get('selected_supplier')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = Purchase.objects.filter(name__icontains=search_key).filter(order_date__range=[start_date, end_date])

    if selected_supplier != "":
        base_query = base_query.filter(supplier__in=selected_supplier.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))

    purchases = base_query.order_by('-order_date')
    paginator = Paginator(purchases, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'purchase/ajax_purchase_grid.html', {'purchases': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_purchases(request):
    checked_contacts = request.POST.get('checked_contacts')
    Purchase.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class PurchasesFavorite(TemplateView):
    model = Purchase
    template_name = "purchase/purchases.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["suppliers"] = Contact.objects.all()
        favor = PurchaseFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_users"] = favor.owner.split(',')
        context["sel_suppliers"] = favor.supplier.split(',')
        context["start_date"] = favor.start_date
        context["end_date"] = favor.end_date

        context["favorites"] = PurchaseFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_purchase_favorite(request):
    selected_supplier = request.POST.get('selected_supplier')
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    count = PurchaseFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = PurchaseFavorite.objects.filter(supplier=selected_supplier, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = PurchaseFavorite(name=name, supplier=selected_supplier, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user)
            favor.save()

            favorites = PurchaseFavorite.objects.filter(user=request.user)
            return render(request, 'purchase/ajax_favor_purchases.html', {'favorites': favorites})

def ajax_delete_purchase_favorite(request):
    del_id = request.POST.get('id')
    PurchaseFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_add_order_item(request):
    if request.method == 'POST':
        add_id = request.POST.get('add_id')
        if str(add_id) == "-1":
            obj = OrderItem(
                purchase_id = request.POST.get('purchase_id'),
                stock_id = request.POST.get('stock_id'),
                order_quantity = request.POST.get('quantity'),
            )
            obj.save()
        else:
            obj = OrderItem.objects.get(id=add_id)
            obj.stock_id = request.POST.get('stock_id')
            obj.order_quantity = request.POST.get('quantity')
            obj.save()

    return JsonResponse({'status': 'ok'})
def ajax_update_income_order_item(request):
    if request.method == 'POST':
        orderitem_id = request.POST.get('orderitem_id')
        income_add_id = request.POST.get('income_add_id')
        income_date = request.POST.get('income_date')
        income_quantity = request.POST.get('income_quantity')
        income_description = request.POST.get('income_description')

        if str(income_add_id) == "-1":
            obj = OrderIncomeValid(orderitem_id=orderitem_id, income_date=income_date, income_quantity=income_quantity, income_description=income_description)
            obj.save()
        else:
            obj = OrderIncomeValid.objects.get(id=income_add_id)
            obj.income_date = request.POST.get('income_date')
            obj.income_quantity = request.POST.get('income_quantity')
            obj.income_description = request.POST.get('income_description')
            obj.save()
    return JsonResponse({'status': 'ok'})

def ajax_update_valid_order_item(request):
    if request.method == 'POST':
        valid_id = request.POST.get('valid_id')
        obj = OrderIncomeValid.objects.get(id=valid_id)
        obj.valid_date = request.POST.get('valid_date')
        obj.valid_quantity = request.POST.get('valid_quantity')
        obj.valid_description = request.POST.get('valid_description')
        obj.save()
    return JsonResponse({'status': 'ok'})

def ajax_grid_order_item(request):
    purchase_id = request.POST.get('purchase_id')
    
    items = OrderItem.objects.filter(purchase_id=purchase_id).order_by('id')
    for item in items:
        item.childs = OrderIncomeValid.objects.filter(orderitem_id=item.id)
        item.income_sum = OrderIncomeValid.objects.filter(orderitem_id=item.id).aggregate(Sum('income_quantity'))["income_quantity__sum"]
        item.valid_sum = OrderIncomeValid.objects.filter(orderitem_id=item.id).aggregate(Sum('valid_quantity'))["valid_quantity__sum"]
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'purchase/ajax_order_item_grid.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_list_order_item(request):
    purchase_id = request.POST.get('purchase_id')
    
    items = OrderItem.objects.filter(purchase_id=purchase_id).order_by('id')
    for item in items:
        item.childs = OrderIncomeValid.objects.filter(orderitem_id=item.id)
        item.income_sum = OrderIncomeValid.objects.filter(orderitem_id=item.id).aggregate(Sum('income_quantity'))["income_quantity__sum"]
        item.valid_sum = OrderIncomeValid.objects.filter(orderitem_id=item.id).aggregate(Sum('valid_quantity'))["valid_quantity__sum"]
        
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'purchase/ajax_order_item_list.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_order_item(request):
    checked_stocks = request.POST.get('checked_stocks')
    OrderItem.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

####### brokens ########
@method_decorator(login_required, name='dispatch')
class Brokens(TemplateView):
    model = Purchase
    template_name = "broken/brokens.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = Stock.objects.all()
        context["sel_stocks"] = []
        context["suppliers"] = Contact.objects.all()
        context["sel_suppliers"] = []
        
        context["favorites"] = BrokenFavorite.objects.filter(user=self.request.user)
        return context


def ajax_list_brokens(request):
    search_key = request.POST.get('search_key')
    selected_supplier = request.POST.get('selected_supplier')
    selected_stock = request.POST.get('selected_stock')
    
    base_query = OrderIncomeValid.objects.filter(refund_flag=False).filter(Q(orderitem__stock__name__icontains=search_key) | Q(orderitem__purchase__supplier__name__icontains=search_key))
    if selected_supplier != "":
        base_query = base_query.filter(orderitem__purchase__supplier__in=selected_supplier.split(','))
    if selected_stock != "":
        base_query = base_query.filter(orderitem__stock__in=selected_stock.split(','))

    base_query = base_query.values('orderitem__purchase__supplier', 'orderitem__stock').annotate(broken_sum=Sum(F('income_quantity')-F('valid_quantity'))).filter(broken_sum__gt=0).order_by('-broken_sum')
    for item in base_query:
        item["supplier"] = Contact.objects.get(id=item["orderitem__purchase__supplier"])
        item["stock"] = Stock.objects.get(id=item["orderitem__stock"])
        
    brokens = base_query

    paginator = Paginator(brokens, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'broken/ajax_broken_list.html', {'brokens': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_brokens(request):
    search_key = request.POST.get('search_key')
    selected_supplier = request.POST.get('selected_supplier')
    selected_stock = request.POST.get('selected_stock')
    
    base_query = OrderIncomeValid.objects.filter(refund_flag=False).filter(Q(orderitem__stock__name__icontains=search_key) | Q(orderitem__purchase__supplier__name__icontains=search_key))
    if selected_supplier != "":
        base_query = base_query.filter(orderitem__purchase__supplier__in=selected_supplier.split(','))
    if selected_stock != "":
        base_query = base_query.filter(orderitem__stock__in=selected_stock.split(','))

    base_query = base_query.values('orderitem__purchase__supplier', 'orderitem__stock').annotate(broken_sum=Sum(F('income_quantity')-F('valid_quantity'))).filter(broken_sum__gt=0).order_by('-broken_sum')
    for item in base_query:
        item["supplier"] = Contact.objects.get(id=item["orderitem__purchase__supplier"])
        item["stock"] = Stock.objects.get(id=item["orderitem__stock"])
        
    brokens = base_query

    paginator = Paginator(brokens, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'broken/ajax_broken_grid.html', {'brokens': page_obj, 'page_obj': page_obj, 'paginator': paginator})

class BrokenDetail(TemplateView):
    model = Transport
    template_name = "broken/broken_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supplier'] = Contact.objects.get(id=self.kwargs.get('supplier_id'))
        context['stock'] = Stock.objects.get(id=self.kwargs.get('stock_id'))
        
        return context
def ajax_list_broken_detail(request):
    supplier_id = request.POST.get('supplier_id')
    stock_id = request.POST.get('stock_id')
    broken_details = OrderIncomeValid.objects.filter(refund_flag=False).filter(orderitem__purchase__supplier__id=supplier_id, orderitem__stock__id=stock_id)

    paginator = Paginator(broken_details, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'broken/ajax_broken_detail_list.html', {'broken_details': page_obj, 'page_obj': page_obj, 'paginator': paginator})

@method_decorator(login_required, name='dispatch')
class BrokensFavorite(TemplateView):
    model = Purchase
    template_name = "broken/brokens.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        favor = BrokenFavorite.objects.get(id=self.kwargs.get('pk'))
        context["stocks"] = Stock.objects.all()
        context["sel_stocks"] = favor.stock.split(',')
        context["suppliers"] = Contact.objects.all()
        context["sel_suppliers"] = favor.supplier.split(',')
        
        context["favorites"] = BrokenFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_broken_favorite(request):
    selected_supplier = request.POST.get('selected_supplier')
    selected_stock = request.POST.get('selected_stock')
    
    name = request.POST.get('name')
    
    count = BrokenFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = BrokenFavorite.objects.filter(supplier=selected_supplier, stock=selected_stock, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = BrokenFavorite(name=name, supplier=selected_supplier, stock=selected_stock, user=request.user)
            favor.save()

            favorites = BrokenFavorite.objects.filter(user=request.user)
            return render(request, 'broken/ajax_favor_brokens.html', {'favorites': favorites})

def ajax_delete_broken_favorite(request):
    del_id = request.POST.get('id')
    PurchaseFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

##### refund history ##########
class RefundsHistory(TemplateView):
    model = RefundHistory
    template_name = "broken/refund_history.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = Stock.objects.all()
        context["sel_stocks"] = []
        context["suppliers"] = Contact.objects.all()
        context["sel_suppliers"] = []

        today = date.today()
        start_date = RefundHistory.objects.all().aggregate(Min('refund_date'))["refund_date__min"]
        context["start_date"] = today if start_date == None else start_date 
        end_date = RefundHistory.objects.all().aggregate(Max('refund_date'))["refund_date__max"]
        context["end_date"] = today if end_date == None else end_date

        context["favorites"] = RefundFavorite.objects.filter(user=self.request.user)
        return context
def ajax_list_refunds(request):
    search_key = request.POST.get('search_key')
    selected_supplier = request.POST.get('selected_supplier')
    selected_stock = request.POST.get('selected_stock')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    base_query = RefundHistory.objects.filter(Q(stock__name__icontains=search_key) | Q(supplier__name__icontains=search_key)).filter(refund_date__range=[start_date, end_date])
    if selected_supplier != "":
        base_query = base_query.filter(supplier__in=selected_supplier.split(','))
    if selected_stock != "":
        base_query = base_query.filter(stock__in=selected_stock.split(','))

    brokens = base_query.order_by('-refund_date')

    paginator = Paginator(brokens, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'broken/ajax_refund_list.html', {'brokens': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_refunds(request):
    search_key = request.POST.get('search_key')
    selected_supplier = request.POST.get('selected_supplier')
    selected_stock = request.POST.get('selected_stock')
    
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    base_query = RefundHistory.objects.filter(Q(stock__name__icontains=search_key) | Q(supplier__name__icontains=search_key)).filter(refund_date__range=[start_date, end_date])
    if selected_supplier != "":
        base_query = base_query.filter(supplier__in=selected_supplier.split(','))
    if selected_stock != "":
        base_query = base_query.filter(stock__in=selected_stock.split(','))

    brokens = base_query.order_by('-refund_date')

    paginator = Paginator(brokens, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'broken/ajax_refund_grid.html', {'brokens': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_get_brokens_from_date(request):
    stock_id = request.POST.get('stock_id')
    supplier_id = request.POST.get('supplier_id')
    sel_date = request.POST.get('sel_date')
    
    base_query = OrderIncomeValid.objects.filter(refund_flag=False).filter(orderitem__purchase__supplier__id=supplier_id, orderitem__stock__id=stock_id).filter(valid_date__lte=sel_date)
    
    base_query = base_query.aggregate(broken_sum=Sum(F('income_quantity')-F('valid_quantity')))["broken_sum"]
    
    return JsonResponse({'status': 'ok', 'broken_sum': base_query})

def ajax_add_broken_refund(request):
    stock_id = request.POST.get('stock_id')
    supplier_id = request.POST.get('supplier_id')
    sel_date = request.POST.get('sel_date')
    quantity = request.POST.get('quantity')
    description = request.POST.get('description')
    user_id = request.POST.get('user_id')
    
    obj = RefundHistory(stock_id=stock_id, supplier_id=supplier_id, description=description, quantity=quantity, refund_date=sel_date, user_id=user_id)
    obj.save()

    base_query = OrderIncomeValid.objects.filter(orderitem__purchase__supplier__id=supplier_id, orderitem__stock__id=stock_id).filter(valid_date__lte=sel_date)
    base_query.update(refund_flag=True)

    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class RefundsFavorite(TemplateView):
    model = RefundHistory
    template_name = "broken/refund_history.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        favor = RefundFavorite.objects.get(id=self.kwargs.get('pk'))
        context["stocks"] = Stock.objects.all()
        context["sel_stocks"] = favor.stock.split(',')
        context["suppliers"] = Contact.objects.all()
        context["sel_suppliers"] = favor.supplier.split(',')
        context["start_date"] = favor.start_date
        context["end_date"] = favor.end_date

        context["favorites"] = RefundFavorite.objects.filter(user=self.request.user)
        return context
def ajax_add_refund_favorite(request):
    selected_supplier = request.POST.get('selected_supplier')
    selected_stock = request.POST.get('selected_stock')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    name = request.POST.get('name')
    
    count = RefundFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = RefundFavorite.objects.filter(supplier=selected_supplier, stock=selected_stock, start_date=start_date, end_date=end_date, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = RefundFavorite(name=name, supplier=selected_supplier, stock=selected_stock, start_date=start_date, end_date=end_date, user=request.user)
            favor.save()

            favorites = RefundFavorite.objects.filter(user=request.user)
            return render(request, 'broken/ajax_favor_refunds.html', {'favorites': favorites})

def ajax_delete_refund_favorite(request):
    del_id = request.POST.get('id')
    RefundFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

####### transports ########
@method_decorator(login_required, name='dispatch')
class Transports(TemplateView):
    model = Purchase
    template_name = "transport/transports.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        context["suppliers"] = Contact.objects.all()
        context["sel_suppliers"] = []

        today = date.today()
        dep_start_date = Transport.objects.all().aggregate(Min('departure'))["departure__min"]
        context["dep_start_date"] = today if dep_start_date == None else dep_start_date 
        dep_end_date = Transport.objects.all().aggregate(Max('departure'))["departure__max"]
        context["dep_end_date"] = today if dep_end_date == None else dep_end_date
        
        arr_start_date = Transport.objects.all().aggregate(Min('arrival'))["arrival__min"]
        context["arr_start_date"] = today if arr_start_date == None else arr_start_date 
        arr_end_date = Transport.objects.all().aggregate(Max('arrival'))["arrival__max"]
        context["arr_end_date"] = today if arr_end_date == None else arr_end_date

        context["favorites"] = TransportFavorite.objects.filter(user=self.request.user)
        return context

@method_decorator(login_required, name='dispatch')
class TransportAdd(CreateView):
    model = Transport
    form_class = TransportForm
    template_name = "transport/transport_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["purchases"] = Purchase.objects.filter()
        return context
    def get_success_url(self):
        return reverse('transports')

@method_decorator(login_required, name='dispatch')
class TransportUpdate(UpdateView):
    model = Transport
    form_class = TransportForm
    template_name = "transport/transport_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["purchases"] = Purchase.objects.filter()
        transport = Transport.objects.get(pk=self.kwargs.get('pk'))
        context['transport'] = transport
        return context
    def get_success_url(self):
        return reverse('detail-transport', kwargs={'pk': self.kwargs.get('pk')})

def ajax_transport_new_detail(request):
    purchase_id = request.POST.get('purchase_id')

    purchase = Purchase.objects.get(id=purchase_id)
    items = OrderItem.objects.filter(purchase_id=purchase_id).order_by('id')
    for item in items:
        item.childs = OrderIncomeValid.objects.filter(orderitem_id=item.id)
        item.income_sum = OrderIncomeValid.objects.filter(orderitem_id=item.id).aggregate(Sum('income_quantity'))["income_quantity__sum"]
        item.valid_sum = OrderIncomeValid.objects.filter(orderitem_id=item.id).aggregate(Sum('valid_quantity'))["valid_quantity__sum"]

    return render(request, 'transport/ajax_transport_new_detail.html', {'items': items, 'purchase': purchase})

def ajax_list_transports(request):
    search_key = request.POST.get('search_key')
    selected_supplier = request.POST.get('selected_supplier')
    selected_owner = request.POST.get('selected_owner')

    dep_start_date = request.POST.get('dep_start_date')
    dep_end_date = request.POST.get('dep_end_date')
    arr_start_date = request.POST.get('arr_start_date')
    arr_end_date = request.POST.get('arr_end_date')

    base_query = Transport.objects.filter(name__icontains=search_key).filter(departure__range=[dep_start_date, dep_end_date]).filter(arrival__range=[arr_start_date, arr_end_date])

    if selected_supplier != "":
        base_query = base_query.filter(purchase__supplier__in=selected_supplier.split(','))
    if selected_owner != "":
        base_query = base_query.filter(purchase__user__in=selected_owner.split(','))
    
    today = datetime.now().date()
    transports = base_query.order_by('arrival')
    for trans in transports:
        diff_days = (trans.arrival - trans.departure).days
        progress_days = (today - trans.departure).days
        if today >= trans.arrival:
            trans.progress_rate = 100
        else:
            trans.progress_rate = progress_days/diff_days * 100
    
    paginator = Paginator(transports, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'transport/ajax_transport_list.html', {'transports': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_transports(request):
    search_key = request.POST.get('search_key')
    selected_supplier = request.POST.get('selected_supplier')
    selected_owner = request.POST.get('selected_owner')
    dep_start_date = request.POST.get('dep_start_date')
    dep_end_date = request.POST.get('dep_end_date')
    arr_start_date = request.POST.get('arr_start_date')
    arr_end_date = request.POST.get('arr_end_date')

    base_query = Transport.objects.filter(name__icontains=search_key).filter(departure__range=[dep_start_date, dep_end_date]).filter(arrival__range=[arr_start_date, arr_end_date])

    if selected_supplier != "":
        base_query = base_query.filter(purchase__supplier__in=selected_supplier.split(','))
    if selected_owner != "":
        base_query = base_query.filter(purchase__user__in=selected_owner.split(','))

    transports = base_query.order_by('arrival')

    paginator = Paginator(transports, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'transport/ajax_transport_grid.html', {'transports': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_transports(request):
    checked_contacts = request.POST.get('checked_contacts')
    Transport.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

class TransportDetail(TemplateView):
    model = Transport
    template_name = "transport/transport_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transport = Transport.objects.get(pk=self.kwargs.get('pk'))
        context['transport'] = transport
        
        items = OrderItem.objects.filter(purchase_id=transport.purchase.id).order_by('id')
        for item in items:
            item.childs = OrderIncomeValid.objects.filter(orderitem_id=item.id)
            item.income_sum = OrderIncomeValid.objects.filter(orderitem_id=item.id).aggregate(Sum('income_quantity'))["income_quantity__sum"]
            item.valid_sum = OrderIncomeValid.objects.filter(orderitem_id=item.id).aggregate(Sum('valid_quantity'))["valid_quantity__sum"]

        filtered_ids = OrderItem.objects.filter(purchase_id=transport.purchase.id).values('stock').distinct().order_by()
        context["items"] = items
        context["stocks"] = Stock.objects.filter(id__in=filtered_ids)
        context['transport_order_item'] = OrderItem.objects.filter(purchase_id=self.kwargs.get('pk'))
        return context

def ajax_add_departure_item(request):
    if request.method == 'POST':
        add_id = request.POST.get('add_id')
        if str(add_id) == "-1":
            obj = DepatureItem(
                transport_id = request.POST.get('transport_id'),
                stock_id = request.POST.get('stock_id'),
                quantity = request.POST.get('quantity'),
            )
            obj.save()
        else:
            obj = DepatureItem.objects.get(id=add_id)
            obj.stock_id = request.POST.get('stock_id')
            obj.quantity = request.POST.get('quantity')
            obj.save()

    return JsonResponse({'status': 'ok'})

def ajax_grid_departure_item(request):
    transport_id = request.POST.get('transport_id')
    
    items = DepatureItem.objects.filter(transport_id=transport_id).order_by('id')
    
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'transport/ajax_departure_item_grid.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_list_departure_item(request):
    transport_id = request.POST.get('transport_id')
    
    items = DepatureItem.objects.filter(transport_id=transport_id).order_by('id')
        
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'transport/ajax_departure_item_list.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_departure_item(request):
    checked_stocks = request.POST.get('checked_stocks')
    DepatureItem.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class TransportsFavorite(TemplateView):
    model = Transport
    template_name = "transport/transports.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favor = TransportFavorite.objects.get(id=self.kwargs.get('pk'))
        
        context["users"] = User.objects.all()
        context["sel_users"] = favor.owner.split(',')
        context["suppliers"] = Contact.objects.all()
        context["sel_suppliers"] = favor.supplier.split(',')
        
        context["dep_start_date"] = favor.dep_start_date
        context["dep_end_date"] = favor.dep_end_date
        context["arr_start_date"] = favor.arr_start_date
        context["arr_end_date"] = favor.arr_end_date
        
        context["favorites"] = TransportFavorite.objects.filter(user=self.request.user)
        return context


def ajax_add_transport_favorite(request):
    selected_supplier = request.POST.get('selected_supplier')
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')
    dep_start_date = request.POST.get('dep_start_date')
    dep_end_date = request.POST.get('dep_end_date')
    arr_start_date = request.POST.get('arr_start_date')
    arr_end_date = request.POST.get('arr_end_date')

    count = TransportFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = TransportFavorite.objects.filter(supplier=selected_supplier, owner=selected_owner, dep_start_date=dep_start_date, dep_end_date=dep_end_date, arr_start_date=arr_start_date, arr_end_date=arr_end_date, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = TransportFavorite(name=name, supplier=selected_supplier, owner=selected_owner, dep_start_date=dep_start_date, dep_end_date=dep_end_date, arr_start_date=arr_start_date, arr_end_date=arr_end_date, user=request.user)
            favor.save()

            favorites = TransportFavorite.objects.filter(user=request.user)
            return render(request, 'transport/ajax_favor_transports.html', {'favorites': favorites})

def ajax_delete_transport_favorite(request):
    del_id = request.POST.get('id')
    TransportFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})
