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

from backend.models import User, Stock
from purchase.models import Purchase

from .models import AdjustItem, AdjustFavorite

from datetime import date
from datetime import datetime
import odoorpc
import pytz
from django.shortcuts import render, redirect
import pandas as pd

# adjusts
@method_decorator(login_required, name='dispatch')
class Adjusts(TemplateView):
    model = AdjustItem
    template_name = "adjust/adjusts.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        context["stocks"] = Stock.objects.all()
        context["sel_stocks"] = []

        today = date.today()
        start_date = AdjustItem.objects.all().aggregate(Min('adjust_date'))["adjust_date__min"]
        context["start_date"] = today if start_date == None else start_date 
        end_date = AdjustItem.objects.all().aggregate(Max('adjust_date'))["adjust_date__max"]
        context["end_date"] = today if end_date == None else end_date

        context["favorites"] = AdjustFavorite.objects.filter(user=self.request.user)
        return context

def ajax_odoo_get_adjust(request):
    stocks = Stock.objects.all()
    # Prepare the connection to the server
    odoo = odoorpc.ODOO('temoes.odoo.com',  protocol='jsonrpc+ssl', port=443)
    # Login
    odoo.login('temoes', 'tpogorov@gmail.com', 'hijacker2020')
    saledata = []
    purchasedata = []
    utc=pytz.UTC

    if 'sale.order' in odoo.env:
        Order = odoo.env['sale.order']
        order_ids = Order.search([])
        for order in Order.browse(order_ids):
            for line in order.order_line:
                if line.product_id.default_code:
                    saledata.append({
                        "internal": line.product_id.default_code,
                        "quantity": line.product_uom_qty,
                        "date": line.create_date,
                    })


    #Getting Purchase Data .....
    if 'purchase.order' in odoo.env:
        Purchase_ = odoo.env['purchase.order']
        order_ids = Purchase_.search([])
        for order in Purchase_.browse(order_ids):
            for line in order.order_line:
                if line.product_id.default_code:
                    purchasedata.append({
                        "internal": line.product_id.default_code,
                        "quantity": line.product_uom_qty,
                        "date": line.create_date,
                    })
    sale_filter = []
    purchase_filter = []
    for stoc in stocks:
        for ref in saledata:
            if ref['internal'].strip() == stoc.reference and utc.localize(ref['date'])>= stoc.date:
                sale_filter.append({
                    "internal": ref['internal'],
                    "quantity": ref['quantity'],
                })
        for pur_ref in purchasedata:
            if pur_ref['internal'].strip() == stoc.reference and utc.localize(pur_ref['date'])>= stoc.date:
                purchase_filter.append({
                    "internal": pur_ref['internal'],
                    "quantity": -pur_ref['quantity'],
                })
    all_data = sale_filter + purchase_filter

    if not all_data:
        pass

    else:

        df = pd.DataFrame(all_data)
        g = df.groupby('internal', as_index=False).sum()
        d = g.to_dict('r')
        for stoc in stocks:
            for d_item in d:
                if stoc.reference == d_item['internal'].strip():
                    stocks_date = Stock.objects.get(id=stoc.id)
                    stocks_date.date = datetime.now()
                    stocks_date.save()
                    current_qt = stoc.quantity
                    adjust_qt = stoc.quantity + d_item['quantity']
                
                    # count = AdjustItem.objects.filter(stock_id=stoc.id, adjust_date=datetime.now()).count()
                    # print(count)
                    obj = AdjustItem(name=stoc.name, description="", stock_id=stoc.id, adjust_date=datetime.now(), current_qt=current_qt, adjust_qt=adjust_qt, quantity=d_item['quantity'], user=request.user)
                    obj.save()
                
    return redirect('adjusts')


def ajax_add_adjust(request):
    name = request.POST.get('name')
    adjust_date = request.POST.get('date')
    description = request.POST.get('description')
    stock_id = request.POST.get('stock')
    current_qt = request.POST.get('current_qt')
    adjust_qt = request.POST.get('adjust_qt')
    add_id = request.POST.get('add_id')

    quantity = int(adjust_qt) - int(current_qt)
    
    if str(add_id) == "-1": 
        count = AdjustItem.objects.filter(stock_id=stock_id, adjust_date=adjust_date).count()
        if count != 0:
            return JsonResponse({'err_code': '1'})
        else:
            obj = AdjustItem(name=name, description=description, stock_id=stock_id, adjust_date=adjust_date, current_qt=current_qt, adjust_qt=adjust_qt, quantity=quantity, user=request.user)
            obj.save()
            return JsonResponse({'err_code': '2', 'adjust_id': obj.id})
    else:
        obj = AdjustItem.objects.get(id=add_id)
        obj.name = name
        obj.stock_id = stock_id
        obj.adjust_date = adjust_date
        obj.description = description
        obj.current_qt = current_qt
        obj.adjust_qt = adjust_qt
        obj.quantity = quantity
        obj.save()
        return JsonResponse({'err_code': '2', 'adjust_id': obj.id})

def ajax_list_adjusts(request):
    search_key = request.POST.get('search_key')
    selected_stock = request.POST.get('selected_stock')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = AdjustItem.objects.filter(name__icontains=search_key).filter(adjust_date__range=[start_date, end_date])

    if selected_stock != "":
        base_query = base_query.filter(stock__in=selected_stock.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))
    
    adjusts = base_query.order_by('-adjust_date')
    
    paginator = Paginator(adjusts, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    
    return render(request, 'adjust/ajax_adjust_list.html', {'adjusts': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_adjusts(request):
    search_key = request.POST.get('search_key')
    selected_stock = request.POST.get('selected_stock')
    selected_owner = request.POST.get('selected_owner')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    base_query = AdjustItem.objects.filter(name__icontains=search_key).filter(adjust_date__range=[start_date, end_date])

    if selected_stock != "":
        base_query = base_query.filter(stock__in=selected_stock.split(','))
    if selected_owner != "":
        base_query = base_query.filter(user__in=selected_owner.split(','))

    adjusts = base_query.order_by('-adjust_date')
    paginator = Paginator(adjusts, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'adjust/ajax_adjust_grid.html', {'adjusts': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_adjusts(request):
    checked_contacts = request.POST.get('checked_contacts')
    AdjustItem.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class AdjustsFavorite(TemplateView):
    model = AdjustItem
    template_name = "adjust/adjusts.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["stocks"] = Stock.objects.all()
        favor = AdjustFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_users"] = favor.owner.split(',')
        context["sel_stocks"] = favor.stock.split(',')
        context["start_date"] = favor.start_date
        context["end_date"] = favor.end_date

        context["favorites"] = AdjustFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_adjust_favorite(request):
    selected_stock = request.POST.get('selected_stock')
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    count = AdjustFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = AdjustFavorite.objects.filter(stock=selected_stock, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = AdjustFavorite(name=name, stock=selected_stock, owner=selected_owner, start_date=start_date, end_date=end_date, user=request.user)
            favor.save()

            favorites = AdjustFavorite.objects.filter(user=request.user)
            return render(request, 'adjust/ajax_favor_adjusts.html', {'favorites': favorites})

def ajax_delete_adjust_favorite(request):
    del_id = request.POST.get('id')
    AdjustFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_get_current_quantity(request):
    stock_id = request.POST.get('stock_id')
    adjust_date = request.POST.get('adjust_date')

    current_qt = 0
    # raw_query # yangyang
    str_query = "SELECT id, quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
        SELECT id, quantity from backend_stock WHERE id=" + str(stock_id) + "\
        UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id WHERE I.stock_id="+ str(stock_id) + " and C.date <= '"+ adjust_date +"' group by I.stock_id \
        UNION ALL SELECT group_id as id, SUM(quantity) as quantity FROM backend_command WHERE finished=3 and group_id="+ str(stock_id) + " and date <= '"+ adjust_date +"' group by group_id\
        UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id WHERE P.stock_id="+str(stock_id)+ " and V.valid_date <= '"+ adjust_date +"' group by P.stock_id\
        UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' and OI.stock_id='"+str(stock_id)+"' and O.order_date <= '"+ adjust_date +"' group by OI.stock_id\
        UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem WHERE stock_id="+ str(stock_id) + " group by stock_id\
        ) GROUP BY id)"
    tmp = Stock.objects.raw(str_query)
    
    for temp in tmp:
        current_qt = temp.quantity
    if current_qt is None:
        current_qt = 0
    return JsonResponse({'current_qt': current_qt})

def ajax_adjust_stock(request):
    name = request.POST.get('name')
    adjust_date = date.today().strftime('%Y-%m-%d')
    description = request.POST.get('description')
    stock_id = request.POST.get('stock')
    current_qt = request.POST.get('current_qt')
    adjust_qt = request.POST.get('adjust_qt')
    
    quantity = int(adjust_qt) - int(current_qt)
    
    count = AdjustItem.objects.filter(stock_id=stock_id, adjust_date=adjust_date).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        obj = AdjustItem(name=name, description=description, stock_id=stock_id, adjust_date=adjust_date, current_qt=current_qt, adjust_qt=adjust_qt, quantity=quantity, user=request.user)
        obj.save()
        return JsonResponse({'err_code': '2', 'adjust_id': obj.id})