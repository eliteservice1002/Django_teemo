from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password


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
from django.shortcuts import render, redirect

from cities_light.models import Country

from .models import User, Category, CsvArchivo, UserRole
from .models import Contact, ContactFavorite
from .models import Client, ClientFavorite, ClientAddress, ClientChatter
from .models import Stock, StockFavorite, SubProduct
from .models import GroupItem, GroupFavorite
from .models import Command, CommandFavorite, CommandWorkerHistory
from .models import BoxFavorite

from .models import WallType, Castor, Color, Mailing, DrawerColor, Location, Strip, Lock, Task, ProviderAdd, Tax, SubContact, MailList

from outcome.models import Outcome
from purchase.models import Purchase, Transport
from job.models import Job, JobCandidate

from .forms import UserForm, StockForm, ContactForm, ClientForm, CommandForm, MailingForm, UserRoleForm

from .resources import ContactResource, LeadResource, ClientResource, StockResource, GroupResource, MailResource

import pandas as pd
import os
import pytz

from datetime import date
from datetime import datetime

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import odoorpc
# from django.core.mail import EmailMessage
# from django.core.mail import send_mail

# Create your views here.
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"
    
    def get_success_url(self):
        return reverse_lazy("index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

class LogoutView(RedirectView):
    url = '/login/'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class Home(TemplateView):
    model = User
    template_name = "dashboard.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supplier'] = Contact.objects.all().count()
        context['lead'] = Client.objects.all().count()
        context['stock'] = Stock.objects.filter(b_group=0).count()
        context['group'] = Stock.objects.filter(b_group=1).count()
        context['command'] = Command.objects.all().count()
        context['outcome'] = Outcome.objects.all().count()
        context['purchase'] = Purchase.objects.all().count()
        context['transport'] = Transport.objects.all().count()
        context['category'] = Category.objects.all().count()
        context['job'] = Job.objects.all().count()
        context['candidate'] = JobCandidate.objects.all().count()
        # raw_query # yangyang
        filtered_ids = Stock.objects.filter(b_group=0).values_list('id', flat=True)
        str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium, SUM(quantity-minium) as reminder  FROM (\
                SELECT id, quantity, minium from backend_stock \
                UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity, 0 as minium FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
                UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity, 0 as minium FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id group by P.stock_id\
                UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity, 0 as minium FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
                UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
                ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") Order by reminder ASC limit 0, 5"
        stocks = Stock.objects.raw(str_query)
        context['stocks'] = stocks
        
        # raw_query # yangyang
        filtered_ids = Stock.objects.filter(b_group=1).values_list('id', flat=True)
        str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium, SUM(quantity-minium) as reminder FROM (\
            SELECT id, quantity, minium from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity, 0 as minium FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity, 0 as minium FROM backend_command WHERE finished=3 group by group_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity, 0 as minium FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") order by reminder ASC limit 0, 5"
        groups = Stock.objects.raw(str_query)
        context['groups'] = groups

        return context

@method_decorator(login_required, name='dispatch')
class Profile(UpdateView):
    model = User
    form_class = UserForm
    template_name = "profile.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = User.objects.get(pk=self.kwargs.get('pk'))
        return context
    def get_success_url(self):
        return reverse('profile', kwargs={'pk': self.object.pk})

@method_decorator(login_required, name='dispatch')
class Users(TemplateView):
    model = User
    template_name = "users.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter()
        return context

def ajax_delete_user(request):
    user_id = request.POST.get('del_id')
    user = User.objects.get(id=user_id)
    user.delete()
    return JsonResponse({'status': 'ok'})

def ajax_add_user(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    email_qs = User.objects.filter(email = email)
    if email_qs.exists():
    	return JsonResponse({'err_code': '1'})

    password = make_password(password)
    user = User(
        email = email,
        username = username,
        password = password
    )
    user.save()
    role = UserRole(supplier_add=False, supplier_up=False, supplier_del=False, lead_add=False, lead_up=False, lead_del=False, mail_add=False, mail_up=False, mail_del=False,product_add=False, product_up=False, product_del=False,purchase_add=False, purchase_up=False, purchase_del=False,transport_add=False, transport_up=False, transport_del=False,manufact_add=False, manufact_up=False, manufact_del=False,outcome_add=False, outcome_up=False, outcome_del=False,trolley_add=False, trolley_up=False, trolley_del=False,invent_add=False, invent_up=False, invent_del=False,offer_add=False, offer_up=False, offer_del=False, time_add=False, time_up=False, time_del=False,setting_add=False, setting_up=False, setting_del=False)
    role.save()
    user.role_id = role.pk
    user.save()
    
    return JsonResponse({'err_code': '2'})

@method_decorator(login_required, name='dispatch')
class Role(UpdateView):
    model = UserRole
    form_class = UserRoleForm
    template_name = "role.html"
    success_url = reverse_lazy('users')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = UserRole.objects.get(pk=self.kwargs.get('pk'))
        return context

def ajax_update_user(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    phone = request.POST.get('phone')
    edit_id = request.POST.get('edit_id')

    email_qs = User.objects.filter(email = email).exclude(id=edit_id)
    
    if email_qs.exists():
        return JsonResponse({'err_code': '1'})

    user = User.objects.get(id=edit_id)
    user.username = username
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.phone = phone
    user.save()
    
    return JsonResponse({'err_code': '2'})
def ajax_reset_user(request):
    reset_id = request.POST.get('reset_id')
    password = request.POST.get('password')
    
    password = make_password(password)
    user = User.objects.get(id=reset_id)
    user.password = password
    user.save()
    
    return JsonResponse({'err_code': '2'})

def ajax_reset_user1(request):
    reset_id = request.POST.get('reset_id')
    password = request.POST.get('password')
    old_password = request.POST.get('old_password')
    
    if request.user.check_password(old_password) is False:
        return JsonResponse({'err_code': '1'})
    else:
        request.user.set_password(password)
        request.user.save()
        login(request, request.user)
    # password = make_password(password)
    # user = User.objects.get(id=reset_id)
    # user.password = password
    # user.save()
    
    return JsonResponse({'err_code': '2'})

# suppliers
@method_decorator(login_required, name='dispatch')
class Suppliers(TemplateView):
    model = Contact
    template_name = "supplier/suppliers.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        context["countries"] = Country.objects.all()
        context["sel_countries"] = []
        context["favorites"] = ContactFavorite.objects.filter(user=self.request.user)
        subcontacts = SubContact.objects.filter(contact=None)
        for sub in subcontacts:
            sub.delete()
        return context

class SupplierDetail(TemplateView):
    model = Contact
    template_name = "supplier/supplier_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contact = Contact.objects.get(pk=self.kwargs.get('pk'))
        products = contact.products
        if products != None:
            subproduct_array = []
            for i in range(len(products.split(",")) -1):
                subproducts = SubProduct.objects.get(pk=int(products.split(",")[i]))
                subproduct_array.append(subproducts.name)
            separator = ', '
            temp = separator.join(subproduct_array)
            contact.product = temp
        context['contact'] = contact

        return context
@method_decorator(login_required, name='dispatch')
class SupplierAdd(CreateView):
    model = User
    form_class = ContactForm
    template_name = "supplier/supplier_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context['products'] = SubProduct.objects.all().order_by('name')
        context["sel_products"] = []
        return context
    def get_success_url(self):
        product_list = self.request.POST.getlist('products')
        if len(product_list) > 0:
            separator = ', '
            temp = separator.join(product_list) + ","
            
            contact = Contact.objects.get(pk=self.object.pk)
            contact.products = temp
            contact.save()
            sub_contact = SubContact.objects.filter(contact=None)
            for sub in sub_contact:
                sub.contact_id = self.object.pk
                sub.save()
        return reverse('suppliers')

@method_decorator(login_required, name='dispatch')
class SubProducts(TemplateView):
    model = SubProduct
    template_name = "supplier/supplier_product.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = SubProduct.objects.all()
        
        return context

@method_decorator(login_required, name='dispatch')
class SupplierContactAdd(CreateView):
    model = User
    form_class = ContactForm
    template_name = "supplier/supplier_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context["sel_company"] = self.kwargs.get('pk')
        return context
    def get_success_url(self):

        return reverse('detail-supplier', kwargs={'pk': self.kwargs.get('pk')})
@method_decorator(login_required, name='dispatch')
class SupplierUpdate(UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = "supplier/supplier_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        contact = Contact.objects.get(pk=self.kwargs.get('pk'))
        context['contact'] = contact
        context['products'] = SubProduct.objects.all().order_by('name')
        if contact.products != None:
            subpro = contact.products.split(",")
            subpro_arr = []
            for i in range(len(subpro) - 1):
                subpro_arr.append(subpro[i].strip())
            context["sel_products"] = subpro_arr
        else:
            context["sel_products"] = []
        return context
    def get_success_url(self):
        contact = Contact.objects.get(pk=self.kwargs.get('pk'))
        exist = self.request.POST.get('exist')
        exist_pdf = self.request.POST.get('exist_pdf')
        if exist == 'NO':
            contact.picture = ''
        if exist_pdf == 'NO':
            contact.pdf = ''

        product_list = self.request.POST.getlist('products')
        if len(product_list) > 0:
            separator = ', '
            temp = separator.join(product_list) + ","
            
            contact = Contact.objects.get(pk=self.object.pk)
            contact.products = temp
        contact.save()
        sub_contact = SubContact.objects.filter(contact=None)
        for sub in sub_contact:
            sub.contact_id = self.object.pk
            sub.save()
            
        return reverse('detail-supplier', kwargs={'pk': self.kwargs.get('pk')})

def ajax_get_sub_contact(request):
    contact_id = request.POST.get('contact_id')
    if contact_id != "":
        contacts = SubContact.objects.filter(contact_id=contact_id)
        return render(request, 'supplier/ajax_sub_contact.html', {'contacts_inf': contacts}) 
    else:
        
        contacts = SubContact.objects.filter(contact=None)
        return render(request, 'supplier/ajax_sub_contact.html', {'contacts_inf': contacts}) 

def ajax_get_detail_sub_contact(request):
    contact_id = request.POST.get('contact_id')

    contacts = SubContact.objects.filter(contact_id=contact_id)
    return render(request, 'supplier/ajax_sub_detail_contact.html', {'contacts_inf': contacts}) 

def ajax_get_detail_nest_sub_contact(request):
    contact_id = request.POST.get('contact_id')

    contacts = SubContact.objects.filter(contact_id=contact_id)
    return render(request, 'supplier/ajax_nest_table.html', {'subcontacts': contacts}) 
    

def ajax_add_sub_contact(request):
    subname = request.POST.get('subname')
    subposition = request.POST.get('subposition')
    subemail = request.POST.get('subemail')
    submobile = request.POST.get('submobile')
    contact_id = request.POST.get('contact_id')
    sub_contact_id = request.POST.get('sub_contact_id')
    if sub_contact_id != '-1':
        sub_obj = SubContact.objects.filter(id=int(sub_contact_id))
        if sub_obj.exists():
            sub_object = SubContact.objects.get(id=int(sub_contact_id))
            sub_object.name = subname
            sub_object.position = subposition
            sub_object.email = subemail
            sub_object.mobile = submobile
            sub_object.contact_id = contact_id
            sub_object.save()
    else:
        obj = SubContact(name=subname, contact_id=contact_id, email=subemail, mobile=submobile, position=subposition)
        obj.save()
    
    return JsonResponse({'status': 'ok'}) 

def ajax_delete_sub_contact(request):
    del_id = request.POST.get('del_id')
    SubContact.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})   


def ajax_import_contacts(request):
    
    if request.method == 'POST':
        org_column_names = ["Address", "Name", "NIF", "Country", "Notes", "Telephone", "Mobile", "Email", "Web", "Products", "Company"]
        filename = str(request.FILES['file'])
        existCSV = CsvArchivo.objects.all().count()
        if(existCSV > 0):
            CsvArchivo.objects.get().delete()
        obj = CsvArchivo(
            name = request.FILES['file'],
            file = request.FILES.get('file')
            )
        obj.save()
        current_csv = CsvArchivo.objects.get()
        path_csv = current_csv.file.url
            
        from django.conf import settings
        import urllib.request
        full_url = "http://"+request.META['HTTP_HOST'] + str(path_csv)
        print(full_url, "##########")
        path = "temp.csv"
            
        response = urllib.request.urlretrieve(full_url)
        contents = open(response[0]).read()
        
        f = open(path,'w')
        f.write(contents)
        f.close()

        df = pd.read_csv(path)    
        df.fillna("", inplace=True)
        column_names = list(df)
        dif_len = len(list(set(org_column_names) - set(column_names)))

        if dif_len == 0:
            record_count = len(df.index)
            success_record = 0
            failed_record = 0
            exist_record = 0
            for index, row in df.iterrows():
                
                try:
                    country_instance = Country.objects.get(name=row["Country"])
                except Exception as e:
                    print(e)
                    failed_record += 1
                    continue
                
                if row["Company"] != "":
                    try:
                        company_instance = Contact.objects.get(name=row["Company"], parent=None)
                    except Exception as e:
                        print(e)
                        failed_record += 1
                        continue
                else:
                    company_instance = None

                exist_count = Contact.objects.filter(name=row["Name"]).count()
                if exist_count == 0:
                    try:
                        contact = Contact(
                            name=row["Name"],
                            nif=row["NIF"],
                            email=row["Email"],
                            address=str(row["Address"]),
                            notes=str(row["Notes"]),
                            telephone=str(row["Telephone"]),
                            mobile=str(row["Mobile"]), 
                            web=str(row["Web"]), 
                            products=row["Products"].replace("_", ","), 
                            country=country_instance,
                            parent=company_instance, 
                            user=request.user
                        )
                        contact.save()
                        success_record += 1
                    except Exception as e:
                        print(e)
                        failed_record += 1
                else:
                    try:
                        contact = Contact.objects.get(name=row["Name"])
                        contact.nif = row["NIF"]
                        contact.email = row["Email"]
                        contact.address=str(row["Address"])
                        contact.notes=str(row["Notes"])
                        contact.telephone=str(row["Telephone"])
                        contact.mobile=str(row["Mobile"])
                        contact.web=str(row["Web"])
                        contact.products=row["Products"].replace("_", ",")
                        contact.country=country_instance
                        contact.parent=company_instance 
                        contact.user=request.user
                        contact.save()
                        exist_record += 1
                    except Exception as e:
                        print(e)
                        failed_record += 1
            os.remove(path)
            return JsonResponse({'status':'true','error_code':'0', 'total': record_count, 'success': success_record, 'failed': failed_record, 'exist': exist_record})
        else:
            os.remove(path)
            # column count is not equals
            return JsonResponse({'status':'false','error_code':'1'})
    return HttpResponse("Ok")

def ajax_export_contacts(request):
    resource = ContactResource()
    dataset = resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'
    return response

def ajax_list_contacts(request):
    search_key = request.POST.get('search_key')
    selected_country = request.POST.get('selected_country')
    selected_owner = request.POST.get('selected_owner')

    if selected_country == "" and selected_owner == "":
        contacts =  Contact.objects.filter(name__icontains=search_key)
    else:
        if selected_country == "" and selected_owner != "":
            contacts =  Contact.objects.filter(name__icontains=search_key).filter(user__in=selected_owner.split(','))  
        elif selected_country != "" and selected_owner == "":
            contacts =  Contact.objects.filter(name__icontains=search_key).filter(country__in=selected_country.split(','))     
        else:
            contacts =  Contact.objects.filter(name__icontains=search_key).filter(country__in=selected_country.split(',')).filter(user__in=selected_owner.split(',')) 
        
    for con in contacts:
        products = con.products
        if products != None:
            subproduct_array = []
            for i in range(len(products.split(",")) -1):
                subproducts = SubProduct.objects.get(pk=int(products.split(",")[i]))
                subproduct_array.append(subproducts.name)
            separator = ', '
            temp = separator.join(subproduct_array)
            con.product = temp


    paginator = Paginator(contacts, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'supplier/ajax_contact_list.html', {'contacts': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_subproduct_list(request):
    my_id = request.POST.get("sub_id")
    search_key = str(my_id) + ","
    contacts = Contact.objects.filter(products__contains=search_key)
    subproduct = SubProduct.objects.get(id=my_id)

    return render(request, 'supplier/subproduct_detail.html', {'contacts': contacts, 'select_product_name': subproduct.name})

def ajax_grid_contacts(request):
    search_key = request.POST.get('search_key')
    selected_country = request.POST.get('selected_country')
    selected_owner = request.POST.get('selected_owner')
    
    if selected_country == "" and selected_owner == "":
        contacts =  Contact.objects.filter(name__icontains=search_key)
    else:
        if selected_country == "" and selected_owner != "":
            contacts =  Contact.objects.filter(name__icontains=search_key).filter(user__in=selected_owner.split(','))  
        elif selected_country != "" and selected_owner == "":
            contacts =  Contact.objects.filter(name__icontains=search_key).filter(country__in=selected_country.split(','))     
        else:
            contacts =  Contact.objects.filter(name__icontains=search_key).filter(country__in=selected_country.split(',')).filter(user__in=selected_owner.split(','))     
    
    paginator = Paginator(contacts, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'supplier/ajax_contact_grid.html', {'contacts': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_contacts(request):
    checked_contacts = request.POST.get('checked_contacts')
    Contact.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class SuppliersFavorite(TemplateView):
    model = Contact
    template_name = "supplier/suppliers.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["countries"] = Country.objects.all()
        favor = ContactFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_users"] = favor.owner.split(',')
        context["sel_countries"] = favor.country.split(',')
        

        context["favorites"] = ContactFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_contact_favorite(request):
    selected_country = request.POST.get('selected_country')
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')

    count = ContactFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = ContactFavorite.objects.filter(country=selected_country, owner=selected_owner, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = ContactFavorite(name=name, country=selected_country, owner=selected_owner, user=request.user)
            favor.save()

            favorites = ContactFavorite.objects.filter(user=request.user)
            return render(request, 'supplier/ajax_favor_contacts.html', {'favorites': favorites})

def ajax_delete_contact_favorite(request):
    del_id = request.POST.get('id')
    ContactFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})


# leads
@method_decorator(login_required, name='dispatch')
class Leads(TemplateView):
    model = Client
    template_name = "lead/leads.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["sel_users"] = []
        context["countries"] = Country.objects.all()
        context["sel_countries"] = []
        context["all_leads"] = Client.objects.all()
        context["favorites"] = ClientFavorite.objects.filter(user=self.request.user)
        return context

class LeadDetail(TemplateView):
    model = Client
    template_name = "lead/lead_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chatter = ClientChatter.objects.filter(client_id=self.kwargs.get('pk')).order_by("-date")[:5]
        contact = Client.objects.get(pk=self.kwargs.get('pk'))
        context['chatter'] = chatter
        context['contact'] = contact
        child_contacts = Client.objects.filter(parent_id=self.kwargs.get('pk'))

        maillists = contact.mail_list
        if maillists != None:
            maillists_array = []
            for i in range(len(maillists.split(",")) -1):
                mail_v = MailList.objects.filter(pk=int(maillists.split(",")[i]))
                if mail_v.exists():
                    mailtemp = MailList.objects.get(pk=int(maillists.split(",")[i]))
                    maillists_array.append(mailtemp.name)
            separator = ', '
            temp = separator.join(maillists_array)
            contact.maillists = temp
        for child in child_contacts:
            child_mail = child.mail_list
            if child_mail != None:
                maillists_array = []
                for i in range(len(child_mail.split(",")) -1):
                    mail_v = MailList.objects.filter(pk=int(child_mail.split(",")[i]))
                    if mail_v.exists():
                        mailtemp = MailList.objects.get(pk=int(child_mail.split(",")[i]))
                        maillists_array.append(mailtemp.name)
                separator = ', '
                temp = separator.join(maillists_array)
                child.submailtag = temp
        context['child_contacts'] = child_contacts
        return context
@method_decorator(login_required, name='dispatch')
class LeadAdd(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "lead/lead_new.html"

    def get_success_url(self):
        
        return reverse_lazy("leads")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context["companies"] = Client.objects.filter(parent=None)
        context['maillists'] = MailList.objects.all().order_by('name')
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            if contact.parent != None:
                contact.b_client = contact.parent.b_client
            
            contact.save()
            mail_list = self.request.POST.getlist('maillists')
            if len(mail_list) > 0:
                separator = ', '
                temp = separator.join(mail_list) + ","
                
                client = Client.objects.get(pk=contact.id)
                client.mail_list = temp
                client.save()
            clientchatter = ClientChatter(name=contact.name, client_id=contact.id, flag=True)
            clientchatter.save()
            return HttpResponseRedirect(self.get_success_url())

        return render(request, self.template_name, {'form': form})  

    # def get_success_url(self):
    #     contacts = Client.objects.get(pk=self.object.id)
    #     print("---------------------------", contacts.b_client)
    #     # if contacts.exists():
    #     #     contact = Client.objects.get(pk=self.object.id)
    #     #     contact.b_client = contact.parent.b_client
    #     #     contact.save()
    #     return reverse('leads')

@method_decorator(login_required, name='dispatch')
class LeadContactAdd(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "lead/lead_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context["companies"] = Client.objects.filter(parent=None)
        context["sel_company"] = self.kwargs.get('pk')
        context['maillists'] = MailList.objects.all().order_by('name')
        return context
    def get_success_url(self):
        contact = Client.objects.get(pk=self.object.id)
        if contact.parent != None:
            contact.b_client = contact.parent.b_client
            contact.save()
        clientchatter = ClientChatter(name=contact.name, client_id=contact.parent_id, flag=True)
        clientchatter.save()
        return reverse('detail-lead', kwargs={'pk': self.object.id})
@method_decorator(login_required, name='dispatch')
class LeadUpdate(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "lead/lead_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context["companies"] = Client.objects.filter(parent=None)
        contact = Client.objects.get(pk=self.kwargs.get('pk'))
        context['contact'] = contact
        context['maillists'] = MailList.objects.all().order_by('name')
        if contact.mail_list != None:
            submail = contact.mail_list.split(",")
            submail_arr = []
            for i in range(len(submail) - 1):
                submail_arr.append(submail[i].strip())
            context["sel_mailings"] = submail_arr
        else:
            context["sel_mailings"] = []
        return context
    def get_success_url(self):
        contacts = Client.objects.filter(pk=self.object.id)
        
        if contacts.exists():
            contact = Client.objects.get(pk=self.object.id)
            # clientchatter = ClientChatter(name=contact.name, client_id=contact.id, flag=False)
            # clientchatter.save()
            if contact.parent != None:
                contact.b_client = contact.parent.b_client
        exist = self.request.POST.get('exist')
        exist_pdf = self.request.POST.get('exist_pdf')
        if exist == 'NO':
            contact.picture = ''
        if exist_pdf == 'NO':
            contact.pdf = ''
        contact.save()
        mail_list = self.request.POST.getlist('maillists')
        if len(mail_list) > 0:
            separator = ', '
            temp = separator.join(mail_list) + ","
            
            client = Client.objects.get(pk=contact.id)
            client.mail_list = temp
            client.save()

        child_contacts = Client.objects.filter(parent_id=self.kwargs.get('pk'))
        parent_contact = Client.objects.get(id=self.kwargs.get('pk'))
        for child in child_contacts:
            child.mail_list = parent_contact.mail_list
            child.save()

        return reverse('detail-lead', kwargs={'pk': self.object.id})

def ajax_chatter_leads(request):
    if request.method == "POST":

        comment = request.POST.get('comment')
        client = request.POST.get('client')
        clientchatter = ClientChatter(name=comment, pdf=request.FILES.get('file'), pdfname=request.FILES['file'], comment=comment, client_id=client, flag=True)
        clientchatter.save()

        return HttpResponse("Ok")

def ajax_chatter_comment(request):
    if request.method == "POST":
        comment = request.POST.get('comment')
        client = request.POST.get('client')
        clientchatter = ClientChatter(name=comment, comment=comment, client_id=client, flag=True)
        clientchatter.save()

        return HttpResponse("Ok")

def ajax_import_leads(request):
    
    if request.method == 'POST':
        org_column_names = ["name", "nif", "country", "notes", "telephone", "mobile", "email", "web", "products", "company"]
        filename = str(request.FILES['file'])
        existCSV = CsvArchivo.objects.all().count()
        if(existCSV > 0):
            CsvArchivo.objects.get().delete()
        obj = CsvArchivo(
            name = request.FILES['file'],
            file = request.FILES.get('file')
            )
        obj.save()
        current_csv = CsvArchivo.objects.get()
        path_csv = current_csv.file.url
            
        from django.conf import settings
        import urllib.request
        full_url = "http://"+request.META['HTTP_HOST'] + str(path_csv)
        print(full_url, "##########")
        path = "temp.csv"
            
        response = urllib.request.urlretrieve(full_url)
        contents = open(response[0]).read()
        
        f = open(path,'w')
        f.write(contents)
        f.close()

        df = pd.read_csv(path)    
        df.fillna("", inplace=True)
        column_names = list(df)
        dif_len = len(list(set(org_column_names) - set(column_names)))
        print("==========================", dif_len)

        if dif_len == 0:
            record_count = len(df.index)
            success_record = 0
            failed_record = 0
            exist_record = 0
            for index, row in df.iterrows():
                
                try:
                    country_instance = Country.objects.get(name=row["country"])
                except Exception as e:
                    print(e)
                    failed_record += 1
                    continue
                
                if row["company"] != "":
                    try:
                        company_instance = Client.objects.get(name=row["company"], parent=None)
                    except Exception as e:
                        print(e)
                        failed_record += 1
                        continue
                else:
                    company_instance = None

                exist_count = Client.objects.filter(name=row["name"]).count()
                if exist_count == 0:
                    try:
                        contact = Client(
                            name=row["name"],
                            nif=row["nif"],
                            email=row["email"],
                            notes=str(row["notes"]),
                            telephone=str(row["telephone"]),
                            mobile=str(row["mobile"]), 
                            web=str(row["web"]), 
                            products=row["products"].replace("_", ","), 
                            country=country_instance,
                            parent=company_instance, 
                            user=request.user
                        )
                        contact.save()
                        success_record += 1
                    except Exception as e:
                        print(e)
                        failed_record += 1
                else:
                    try:
                        contact = Client.objects.get(name=row["name"])
                        contact.email = row["email"]
                        contact.nif = row["nif"]
                        contact.notes=str(row["notes"])
                        contact.telephone=str(row["telephone"])
                        contact.mobile=str(row["mobile"])
                        contact.web=str(row["web"])
                        contact.products=row["products"].replace("_", ",")
                        contact.country=country_instance
                        contact.parent=company_instance 
                        contact.user=request.user
                        contact.save()
                        exist_record += 1
                    except Exception as e:
                        print(e)
                        failed_record += 1
            os.remove(path)
            return JsonResponse({'status':'true','error_code':'0', 'total': record_count, 'success': success_record, 'failed': failed_record, 'exist': exist_record})
        else:
            os.remove(path)
            # column count is not equals
            return JsonResponse({'status':'false','error_code':'1'})
    return HttpResponse("Ok")

def ajax_export_leads(request):
    resource = LeadResource()
    dataset = resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads.csv"'
    return response

def ajax_export_clients(request):
    resource = ClientResource()
    dataset = resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clients.csv"'
    return response

def ajax_list_leads(request):
    search_key = request.POST.get('search_key')
    selected_country = request.POST.get('selected_country')
    selected_owner = request.POST.get('selected_owner')

    base_query = Client.objects.filter(name__icontains=search_key).exclude(b_client=True).filter(parent=None)
    if selected_owner != "":
        base_query =  base_query.filter(user__in=selected_owner.split(','))  
    if selected_country != "":
        base_query =  base_query.filter(country__in=selected_country.split(','))     

    contacts = base_query

    paginator = Paginator(contacts, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)
    for obj in page_obj:
        obj.childs = Client.objects.filter(parent_id=obj.id)

    return render(request, 'lead/ajax_lead_list.html', {'contacts': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_leads(request):
    search_key = request.POST.get('search_key')
    selected_country = request.POST.get('selected_country')
    selected_owner = request.POST.get('selected_owner')
    
    base_query = Client.objects.filter(name__icontains=search_key).exclude(b_client=True)
    if selected_owner != "":
        base_query =  base_query.filter(user__in=selected_owner.split(','))  
    if selected_country != "":
        base_query =  base_query.filter(country__in=selected_country.split(','))     

    contacts = base_query  
    
    paginator = Paginator(contacts, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lead/ajax_lead_grid.html', {'contacts': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_list_client_leads(request):
    search_key = request.POST.get('search_key')
    selected_country = request.POST.get('selected_country')
    selected_owner = request.POST.get('selected_owner')

    base_query = Client.objects.filter(name__icontains=search_key).filter(b_client=True).filter(parent=None)
    if selected_owner != "":
        base_query =  base_query.filter(user__in=selected_owner.split(','))  
    if selected_country != "":
        base_query =  base_query.filter(country__in=selected_country.split(','))     

    contacts = base_query  
    
    paginator = Paginator(contacts, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    for obj in page_obj:
        obj.childs = Client.objects.filter(parent_id=obj.id)

    return render(request, 'lead/ajax_lead_client_list.html', {'contacts': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_client_leads(request):
    search_key = request.POST.get('search_key')
    selected_country = request.POST.get('selected_country')
    selected_owner = request.POST.get('selected_owner')
    
    base_query = Client.objects.filter(name__icontains=search_key).filter(b_client=True)
    if selected_owner != "":
        base_query =  base_query.filter(user__in=selected_owner.split(','))  
    if selected_country != "":
        base_query =  base_query.filter(country__in=selected_country.split(','))     

    contacts = base_query    
    
    paginator = Paginator(contacts, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lead/ajax_lead_client_grid.html', {'contacts': page_obj, 'page_obj': page_obj, 'paginator': paginator})
def ajax_transform_client_lead(request):
    contact_id = request.POST.get('contact_id')
    b_client = request.POST.get('b_client')
    obj = Client.objects.get(id=contact_id)
    obj.b_client = b_client
    obj.save()
    Client.objects.filter(parent_id=obj.id).update(b_client=b_client)
    return JsonResponse({'status': 'ok'})

def ajax_delete_leads(request):
    checked_contacts = request.POST.get('checked_contacts')
    Client.objects.filter(id__in=checked_contacts.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class LeadsFavorite(TemplateView):
    model = Client
    template_name = "lead/leads.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["countries"] = Country.objects.all()
        favor = ClientFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_users"] = favor.owner.split(',')
        context["sel_countries"] = favor.country.split(',')
        context["all_leads"] = Client.objects.all()

        context["favorites"] = ClientFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_lead_favorite(request):
    selected_country = request.POST.get('selected_country')
    selected_owner = request.POST.get('selected_owner')
    
    name = request.POST.get('name')

    count = ClientFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = ClientFavorite.objects.filter(country=selected_country, owner=selected_owner, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            favor = ClientFavorite(name=name, country=selected_country, owner=selected_owner, user=request.user)
            favor.save()

            favorites = ClientFavorite.objects.filter(user=request.user)
            return render(request, 'lead/ajax_favor_leads.html', {'favorites': favorites})

def ajax_delete_lead_favorite(request):
    del_id = request.POST.get('id')
    ClientFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_send_lead_emails(request):
    from_email = request.POST.get('from_email')
    to_emails = request.POST.getlist('to_email[]')
    subject = request.POST.get('subject')
    html_content = request.POST.get('message')

    # print(html_content)
    # msg = EmailMessage(subject, html_content, from_email, to_email)
    # msg.content_subtype = "html"  # Main content is now text/html
    # msg.send()

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content,
        # for improved deliverability, provide plain text content in addition to html content
        # plain_text_content='Fresh donuts are out of the oven. Get them while they’re hot!',
        is_multiple=True
    )
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code, response.body, response.headers)
    except Exception as e:
        print(e.message)
    return JsonResponse({'status': 'ok'})

def ajax_add_lead_address(request):
    address = request.POST.get('address')
    add_id = request.POST.get('add_id')
    contact_id = request.POST.get('contact_id')
    if str(add_id) == "-1":
        obj = ClientAddress(address=address, client_id=contact_id)
        obj.save()
    else:
        obj = ClientAddress.objects.get(id=add_id)
        obj.address = address
        obj.save()
    clientchatter = ClientChatter(name=address, client_id=contact_id, clientaddress_id=obj.id, flag=True)
    clientchatter.save()
    return JsonResponse({'status': 'ok'}) 

def ajax_get_lead_address(request):
    contact_id = request.POST.get('contact_id')
    address = ClientAddress.objects.filter(client_id=contact_id)
    return render(request, 'lead/ajax_lead_address.html', {'address': address}) 

def ajax_delete_lead_address(request):
    del_id = request.POST.get('del_id')
    ClientAddress.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

# stock
@method_decorator(login_required, name='dispatch')
class Stocks(TemplateView):
    model = Stock
    template_name = "stocks/stocks.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        
        min_quantity = 0
        max_quantity = 0
        # raw_query # yangyang
        filtered_ids = Stock.objects.filter(b_group=0).values_list('id', flat=True)
        
        max_query = "SELECT id, MAX(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity FROM purchase_orderitem as P LEFT JOIN purchase_orderincomevalid as V on V.orderitem_id = P.id group by P.stock_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        max_stock = Stock.objects.raw(max_query)
        for m in max_stock:
            max_quantity = m.quantity
        # raw_query # yangyang
        min_query = "SELECT id, MIN(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id group by P.stock_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        min_stock = Stock.objects.raw(min_query)
        for m in min_stock:
            min_quantity = m.quantity
        
        context["min_quantity"] = min_quantity
        context["max_quantity"] = max_quantity
        context["sel_min_quantity"] = min_quantity
        context["sel_max_quantity"] = max_quantity
        context["sel_categories"] = []
        context["favorites"] = StockFavorite.objects.filter(user=self.request.user)
        
        return context

@method_decorator(login_required, name='dispatch')
class StocksFavorite(TemplateView):
    model = Stock
    template_name = "stocks/stocks.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        
        min_quantity = 0
        max_quantity = 0
        # raw_query # yangyang
        filtered_ids = Stock.objects.filter(b_group=0).values_list('id', flat=True)
        max_query = "SELECT id, MAX(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id group by P.stock_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        max_stock = Stock.objects.raw(max_query)
        for m in max_stock:
            max_quantity = m.quantity
        # raw_query # yangyang
        min_query = "SELECT id, MIN(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id group by P.stock_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        min_stock = Stock.objects.raw(min_query)
        for m in min_stock:
            min_quantity = m.quantity

        context["min_quantity"] = min_quantity
        context["max_quantity"] = max_quantity
        favor = StockFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_min_quantity"] = favor.min_quantity
        context["sel_max_quantity"] = favor.max_quantity
        context["sel_categories"] = favor.category.split(',')
        context["sel_less"] = favor.less
        context["sel_greater"] = favor.greater

        context["favorites"] = StockFavorite.objects.filter(user=self.request.user)
        return context

def ajax_list_stocks(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    
    less = request.POST.get('less')
    greater = request.POST.get('greater')

    preview_query = Stock.objects.filter(b_group=0).filter(Q(name__icontains=search_key) | Q(reference__icontains=search_key))
    if selected_category != "":
        preview_query = preview_query.filter(category_id__in=selected_category.split(','))

    filtered_ids = preview_query.values_list('id', flat=True)
    
    where_qs = ""#" and quantity>=" + str(from_package) + " and quantity<=" + str(to_package) + ""
    if less == "true":
        where_qs = where_qs + " and quantity < minium "
    if greater == "true":
        where_qs = where_qs + " and quantity >= minium "

    # raw_query # yangyang
    str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium FROM (\
            SELECT id, quantity, minium from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity, 0 as minium FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity, 0 as minium FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id group by P.stock_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity, 0 as minium FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ")" + where_qs
    stocks = Stock.objects.raw(str_query)
    
    paginator = Paginator(stocks, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'stocks/ajax_stock_list.html', {'stocks': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_stocks(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')

    less = request.POST.get('less')
    greater = request.POST.get('greater')
    
    preview_query = Stock.objects.filter(b_group=0).filter(Q(name__icontains=search_key) | Q(reference__icontains=search_key))
    if selected_category != "":
        preview_query = preview_query.filter(category_id__in=selected_category.split(','))

    filtered_ids = preview_query.values_list('id', flat=True)
    
    where_qs = " and quantity>=" + str(from_package) + " and quantity<=" + str(to_package) + ""
    if less == "true":
        where_qs = where_qs + " and quantity < minium "
    if greater == "true":
        where_qs = where_qs + " and quantity >= minium "
    # raw_query # yangyang
    str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium FROM (\
            SELECT id, quantity, minium from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity, 0 as minium FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity, 0 as minium FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id group by P.stock_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity, 0 as minium FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ")" + where_qs
    stocks = Stock.objects.raw(str_query)
    
    paginator = Paginator(stocks, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'stocks/ajax_stock_grid.html', {'stocks': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_add_favorite_stocks(request):
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    less = request.POST.get('less')
    greater = request.POST.get('greater')
    name = request.POST.get('name')

    count = StockFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = StockFavorite.objects.filter(category=selected_category, min_quantity=from_package, max_quantity=to_package, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            stock = StockFavorite(name=name, category=selected_category, min_quantity=from_package, max_quantity=to_package, user=request.user, less=less, greater=greater)
            stock.save()

            favorites = StockFavorite.objects.filter(user=request.user)
            return render(request, 'stocks/ajax_favor_stocks.html', {'favorites': favorites})

def ajax_import_stocks(request):
    
    if request.method == 'POST':
        org_column_names = ["Ref", "Name", "Quantity", "Minium", "Location", "Width", "Height", "Depth", "Weight", "Category"]
        filename = str(request.FILES['file'])
        existCSV = CsvArchivo.objects.all().count()
        if(existCSV > 0):
            CsvArchivo.objects.get().delete()
        obj = CsvArchivo(
            name = request.FILES['file'],
            file = request.FILES.get('file')
            )
        obj.save()
        current_csv = CsvArchivo.objects.get()
        path_csv = current_csv.file.url
            
        from django.conf import settings
        import urllib.request
        full_url = "http://"+request.META['HTTP_HOST'] + str(path_csv)
        print(full_url, "##########")
        path = "temp.csv"
            
        response = urllib.request.urlretrieve(full_url)
        contents = open(response[0]).read()
        
        f = open(path,'w')
        f.write(contents)
        f.close()

        df = pd.read_csv(path)    
        df.fillna("", inplace=True)
        column_names = list(df)
        dif_len = len(list(set(org_column_names) - set(column_names)))

        if dif_len == 0:
            record_count = len(df.index)
            success_record = 0
            failed_record = 0
            exist_record = 0
            for index, row in df.iterrows():
                
                try:
                    cate_instance = Category.objects.get(name=row["Category"])
                    loc_instance = Location.objects.get(name=row["Location"])
                except Exception as e:
                    print(e)
                    failed_record += 1
                    continue
                exist_count = Stock.objects.filter(reference=row["Ref"]).count()
                if exist_count == 0:
                    stock = Stock(
                        name=row["Name"], 
                        reference=row["Ref"], 
                        quantity=row["Quantity"], 
                        category=cate_instance, 
                        location=loc_instance,
                        minium=row["Minium"],
                        width=row["Width"],
                        height=row["Height"],
                        depth=row["Depth"],
                        weight=row["Weight"], 
                        user=request.user
                    )
                    stock.save()
                    success_record += 1
                else:
                    stock = Stock.objects.get(reference=row["Ref"])
                    stock.name = row["Name"]
                    stock.quantity = row["Quantity"]
                    stock.location = loc_instance
                    stock.minium = row["Minium"]
                    stock.width = row["Width"]
                    stock.height = row["Height"]
                    stock.depth = row["Depth"]
                    stock.weight = row["Weight"]
                    stock.category = cate_instance
                    stock.user = request.user
                    stock.save()
                    exist_record += 1
            os.remove(path)
            return JsonResponse({'status':'true','error_code':'0', 'total': record_count, 'success': success_record, 'failed': failed_record, 'exist': exist_record})
        else:
            os.remove(path)
            # column count is not equals
            return JsonResponse({'status':'false','error_code':'1'})
    return HttpResponse("Ok")

def ajax_export_stocks(request):
    resource = StockResource()
    dataset = resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stocks.csv"'
    return response

@method_decorator(login_required, name='dispatch')
class StockAdd(CreateView):
    model = Stock
    form_class = StockForm
    template_name = "stocks/stock_old_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter()
        context["locations"] = Location.objects.exclude(b_deleted=True)
        context['taxes'] = Tax.objects.filter()
        return context
    def get_success_url(self):
        return reverse('stocks')

@method_decorator(login_required, name='dispatch')
class StockUpdate(UpdateView):
    model = Stock
    form_class = StockForm
    template_name = "stocks/stock_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter()
        context["locations"] = Location.objects.exclude(b_deleted=True)
        stock = Stock.objects.get(pk=self.kwargs.get('pk'))
        context['stock'] = stock
        context['provider'] = Contact.objects.all()
        context['taxes'] = Tax.objects.filter()
        context['prov'] = ProviderAdd.objects.filter(stock=self.kwargs.get('pk'))
        return context
    def get_success_url(self):
        stock = Stock.objects.get(pk=self.kwargs.get('pk'))
        exist = self.request.POST.get('exist')
        if exist=='NO':
            stock.picture=''
        stock.save()
        return '{}'.format(reverse('update-stock', kwargs={'pk': self.kwargs.get('pk')}))
        
def ajax_quantity(request):
    
    stock_id = request.POST.get('stock_id')
    minium = request.POST.get('minium')
    quantity = request.POST.get('quantity')
    stock_update = Stock.objects.get(pk=stock_id)
    stock_update.quantity = quantity
    stock_update.minium = minium
    stock_update.save()

    return HttpResponse("ok")


@method_decorator(login_required, name='dispatch')
class StockTemp(TemplateView):
    model = Stock
    form_class = StockForm
    template_name = "stocks/stock_edit.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter()
        context["locations"] = Location.objects.exclude(b_deleted=True)
        context['taxes'] = Tax.objects.filter()
        stock = {}
        context['stock'] = stock
        return context

@method_decorator(login_required, name='dispatch')
class StockUpTemp(UpdateView):
    model = Stock
    form_class = StockForm
    template_name = "stocks/stock_up.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter()
        context["locations"] = Location.objects.exclude(b_deleted=True)
        stock = Stock.objects.get(pk=self.kwargs.get('pk'))
        context['stock'] = stock
        context['taxes'] = Tax.objects.filter()
        return context

def ajax_delete_stocks(request):
    checked_stocks = request.POST.get('checked_stocks')
    Stock.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_delete_stock_favorite(request):
    del_id = request.POST.get('id')
    StockFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

#################################################
######## Box
#################################################

@method_decorator(login_required, name='dispatch')
class Boxs(TemplateView):
    model = Stock
    template_name = "boxs/boxs.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        
        min_quantity = 0
        max_quantity = 0
        # raw_query # yangyang
        filtered_ids = Stock.objects.filter(b_group=2).values_list('id', flat=True)
        print(filtered_ids, "######")
        max_query = "SELECT id, MAX(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        max_box = Stock.objects.raw(max_query)
        for m in max_box:
            max_quantity = m.quantity
        # raw_query # yangyang
        min_query = "SELECT id, MIN(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        min_box = Stock.objects.raw(min_query)
        for m in min_box:
            min_quantity = m.quantity
        
        context["min_quantity"] = min_quantity
        context["max_quantity"] = max_quantity
        context["sel_min_quantity"] = min_quantity
        context["sel_max_quantity"] = max_quantity
        context["sel_categories"] = []
        context["favorites"] = BoxFavorite.objects.filter(user=self.request.user)
        return context

@method_decorator(login_required, name='dispatch')
class BoxsFavorite(TemplateView):
    model = Stock
    template_name = "boxs/boxs.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        
        min_quantity = 0
        max_quantity = 0
        # raw_query # yangyang
        filtered_ids = Stock.objects.filter(b_group=2).values_list('id', flat=True)
        max_query = "SELECT id, MAX(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        max_box = Stock.objects.raw(max_query)
        for m in max_box:
            max_quantity = m.quantity
        # raw_query # yangyang
        min_query = "SELECT id, MIN(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        min_box = Stock.objects.raw(min_query)
        for m in min_box:
            min_quantity = m.quantity

        context["min_quantity"] = min_quantity
        context["max_quantity"] = max_quantity
        favor = BoxFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_min_quantity"] = favor.min_quantity
        context["sel_max_quantity"] = favor.max_quantity
        context["sel_categories"] = favor.category.split(',')
        context["sel_less"] = favor.less
        context["sel_greater"] = favor.greater

        context["favorites"] = BoxFavorite.objects.filter(user=self.request.user)
        return context

def ajax_list_boxs(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    
    less = request.POST.get('less')
    greater = request.POST.get('greater')

    preview_query = Stock.objects.filter(b_group=2).filter(Q(name__icontains=search_key) | Q(reference__icontains=search_key))
    if selected_category != "":
        preview_query = preview_query.filter(category_id__in=selected_category.split(','))

    filtered_ids = preview_query.values_list('id', flat=True)
    
    where_qs = " and quantity>=" + str(from_package) + " and quantity<=" + str(to_package) + ""
    if less == "true":
        where_qs = where_qs + " and quantity < minium "
    if greater == "true":
        where_qs = where_qs + " and quantity >= minium "

    # raw_query # yangyang
    str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium FROM (\
            SELECT id, quantity, minium from backend_stock \
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ")" + where_qs
    boxs = Stock.objects.raw(str_query)
    
    paginator = Paginator(boxs, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'boxs/ajax_box_list.html', {'boxs': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_boxs(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')

    less = request.POST.get('less')
    greater = request.POST.get('greater')
    
    preview_query = Stock.objects.filter(b_group=2).filter(Q(name__icontains=search_key) | Q(reference__icontains=search_key))
    if selected_category != "":
        preview_query = preview_query.filter(category_id__in=selected_category.split(','))

    filtered_ids = preview_query.values_list('id', flat=True)
    
    where_qs = " and quantity>=" + str(from_package) + " and quantity<=" + str(to_package) + ""
    if less == "true":
        where_qs = where_qs + " and quantity < minium "
    if greater == "true":
        where_qs = where_qs + " and quantity >= minium "
    # raw_query # yangyang
    str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium FROM (\
            SELECT id, quantity, minium from backend_stock \
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ")" + where_qs
    boxs = Stock.objects.raw(str_query)
    
    paginator = Paginator(boxs, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'boxs/ajax_box_grid.html', {'boxs': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_add_favorite_boxs(request):
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    less = request.POST.get('less')
    greater = request.POST.get('greater')
    name = request.POST.get('name')

    count = BoxFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = BoxFavorite.objects.filter(category=selected_category, min_quantity=from_package, max_quantity=to_package, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            box = BoxFavorite(name=name, category=selected_category, min_quantity=from_package, max_quantity=to_package, user=request.user, less=less, greater=greater)
            box.save()

            favorites = BoxFavorite.objects.filter(user=request.user)
            return render(request, 'boxs/ajax_favor_boxs.html', {'favorites': favorites})

def ajax_import_boxs(request):
    
    if request.method == 'POST':
        org_column_names = ["Ref", "Name", "Quantity", "Minium", "Location", "Width", "Height", "Depth", "Weight", "Category"]
        filename = str(request.FILES['file'])
        existCSV = CsvArchivo.objects.all().count()
        if(existCSV > 0):
            CsvArchivo.objects.get().delete()
        obj = CsvArchivo(
            name = request.FILES['file'],
            file = request.FILES.get('file')
            )
        obj.save()
        current_csv = CsvArchivo.objects.get()
        path_csv = current_csv.file.url
            
        from django.conf import settings
        import urllib.request
        full_url = "http://"+request.META['HTTP_HOST'] + str(path_csv)
        print(full_url, "##########")
        path = "temp.csv"
            
        response = urllib.request.urlretrieve(full_url)
        contents = open(response[0]).read()
        
        f = open(path,'w')
        f.write(contents)
        f.close()

        df = pd.read_csv(path)    
        df.fillna("", inplace=True)
        column_names = list(df)
        dif_len = len(list(set(org_column_names) - set(column_names)))

        if dif_len == 0:
            record_count = len(df.index)
            success_record = 0
            failed_record = 0
            exist_record = 0
            for index, row in df.iterrows():
                
                try:
                    cate_instance = Category.objects.get(name=row["Category"])
                    loc_instance = Location.objects.get(name=row["Location"])
                except Exception as e:
                    print(e)
                    failed_record += 1
                    continue
                exist_count = Box.objects.filter(reference=row["Ref"]).count()
                if exist_count == 0:
                    box = Box(
                        name=row["Name"], 
                        reference=row["Ref"], 
                        quantity=row["Quantity"], 
                        category=cate_instance, 
                        location=loc_instance,
                        minium=row["Minium"],
                        width=row["Width"],
                        height=row["Height"],
                        depth=row["Depth"],
                        weight=row["Weight"], 
                        user=request.user
                    )
                    box.save()
                    success_record += 1
                else:
                    box = Box.objects.get(reference=row["Ref"])
                    box.name = row["Name"]
                    box.quantity = row["Quantity"]
                    box.location = loc_instance
                    box.minium = row["Minium"]
                    box.width = row["Width"]
                    box.height = row["Height"]
                    box.depth = row["Depth"]
                    box.weight = row["Weight"]
                    box.category = cate_instance
                    box.user = request.user
                    box.save()
                    exist_record += 1
            os.remove(path)
            return JsonResponse({'status':'true','error_code':'0', 'total': record_count, 'success': success_record, 'failed': failed_record, 'exist': exist_record})
        else:
            os.remove(path)
            # column count is not equals
            return JsonResponse({'status':'false','error_code':'1'})
    return HttpResponse("Ok")

@method_decorator(login_required, name='dispatch')
class BoxAdd(CreateView):
    model = Stock
    form_class = StockForm
    template_name = "boxs/box_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter()
        return context
    def get_success_url(self):
        return reverse('boxs')

@method_decorator(login_required, name='dispatch')
class BoxUpdate(UpdateView):
    model = Stock
    form_class = StockForm
    template_name = "boxs/box_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter()
        box = Stock.objects.get(pk=self.kwargs.get('pk'))
        context['box'] = box
        return context
    def get_success_url(self):
        box = Stock.objects.get(pk=self.kwargs.get('pk'))
        exist = self.request.POST.get('exist')
        if exist=='NO':
            box.picture=''
        box.save()
        return reverse('boxs')

def ajax_delete_boxs(request):
    checked_boxs = request.POST.get('checked_boxs')
    Stock.objects.filter(id__in=checked_boxs.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_delete_box_favorite(request):
    del_id = request.POST.get('id')
    BoxFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

#############################################
########## categories 
#############################################

@method_decorator(login_required, name='dispatch')
class Categories(TemplateView):
    model = Category
    template_name = "settings/category.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

def ajax_add_category(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    cate_id = request.POST.get('cate_id')
    if cate_id == "-1":
        count = Category.objects.filter(name=name).count()
    else:
        count = Category.objects.filter(name=name).exclude(id=cate_id).count()
    if count == 0:
        if cate_id == "-1":
            cate = Category(name=name, description=description)
            cate.save()
        else:
            cate = Category.objects.get(id=cate_id)
            cate.name = name
            cate.description = description
            cate.save()

    categories = Category.objects.all()
    return render(request, 'settings/ajax_add_category.html', {'categories': categories})

def ajax_add_subproduct(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    prod_id = request.POST.get('prod_id')
    if prod_id == "-1":
        count = SubProduct.objects.filter(name=name).count()
    else:
        count = SubProduct.objects.filter(name=name).exclude(id=prod_id).count()
    if count == 0:
        if prod_id == "-1":
            prod = SubProduct(name=name, description=description)
            prod.save()
        else:
            prod = SubProduct.objects.get(id=prod_id)
            prod.name = name
            prod.description = description
            prod.save()

    products = SubProduct.objects.all()
    return render(request, 'supplier/ajax_add_subproduct.html', {'products': products})

def ajax_add_provider(request):
    name = request.POST.get('name')
    price = request.POST.get('price')
    refer = request.POST.get('refer')
    description = request.POST.get('description')
    stock_ids = request.POST.get('stock_ids')
    provider = ProviderAdd(provider_id=str(name), price=price, description=description, stock_id=str(stock_ids), reference=refer)
    provider.save()
    prov = ProviderAdd.objects.filter(stock=str(stock_ids))
    return render(request, 'stocks/ajax_add_provider.html', {'prov': prov})
 
def ajax_delete_category(request):
    cate_id = request.POST.get('cate_id')
    cate = Category.objects.get(id=cate_id)
    cate.delete()
    return JsonResponse({'status': 'ok'})

def ajax_delete_subproduct(request):
    
    prod_id = request.POST.get('prod_id')
    prod = SubProduct.objects.get(id=prod_id)
    prod.delete()
    return JsonResponse({'status': 'ok'})

#############################################
########## Walls Type 
#############################################

@method_decorator(login_required, name='dispatch')
class WallsType(TemplateView):
    model = WallType
    template_name = "settings/wallstype.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = WallType.objects.exclude(b_deleted=True)
        return context

def ajax_add_wallstype(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    item_id = request.POST.get('item_id')
    if item_id == "-1":
        count = WallType.objects.filter(name=name).exclude(b_deleted=True).count()
    else:
        count = WallType.objects.filter(name=name).exclude(b_deleted=True).exclude(id=item_id).count()
    if count == 0:
        if item_id == "-1":
            item = WallType(name=name, description=description)
            item.save()
        else:
            item = WallType.objects.get(id=item_id)
            item.name = name
            item.description = description
            item.save()

    items = WallType.objects.exclude(b_deleted=True)
    return render(request, 'settings/ajax_add_wallstype.html', {'items': items})
 
def ajax_delete_wallstype(request):
    item_id = request.POST.get('item_id')
    item = WallType.objects.get(id=item_id)
    item.b_deleted = True
    item.save()
    return JsonResponse({'status': 'ok'})

#############################################
########## Castors 
#############################################

@method_decorator(login_required, name='dispatch')
class Castors(TemplateView):
    model = Castor
    template_name = "settings/castor.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Castor.objects.exclude(b_deleted=True)
        return context

def ajax_add_castor(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    item_id = request.POST.get('item_id')
    if item_id == "-1":
        count = Castor.objects.filter(name=name).exclude(b_deleted=True).count()
    else:
        count = Castor.objects.filter(name=name).exclude(b_deleted=True).exclude(id=item_id).count()
    if count == 0:
        if item_id == "-1":
            item = Castor(name=name, description=description)
            item.save()
        else:
            item = Castor.objects.get(id=item_id)
            item.name = name
            item.description = description
            item.save()

    items = Castor.objects.exclude(b_deleted=True)
    return render(request, 'settings/ajax_add_castor.html', {'items': items})
 
def ajax_delete_castor(request):
    item_id = request.POST.get('item_id')
    item = Castor.objects.get(id=item_id)
    item.b_deleted = True
    item.save()
    return JsonResponse({'status': 'ok'})

#############################################
########## Colors 
#############################################

@method_decorator(login_required, name='dispatch')
class Colors(TemplateView):
    model = Color
    template_name = "settings/color.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Color.objects.exclude(b_deleted=True)
        return context

def ajax_add_color(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    item_id = request.POST.get('item_id')
    if item_id == "-1":
        count = Color.objects.filter(name=name).exclude(b_deleted=True).count()
    else:
        count = Color.objects.filter(name=name).exclude(b_deleted=True).exclude(id=item_id).count()
    if count == 0:
        if item_id == "-1":
            item = Color(name=name, description=description)
            item.save()
        else:
            item = Color.objects.get(id=item_id)
            item.name = name
            item.description = description
            item.save()

    items = Color.objects.exclude(b_deleted=True)
    return render(request, 'settings/ajax_add_color.html', {'items': items})
 
def ajax_delete_color(request):
    item_id = request.POST.get('item_id')
    item = Color.objects.get(id=item_id)
    item.b_deleted = True
    item.save()
    return JsonResponse({'status': 'ok'})

#############################################
########## Locks 
#############################################

@method_decorator(login_required, name='dispatch')
class Locks(TemplateView):
    model = Lock
    template_name = "settings/lock.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Lock.objects.exclude(b_deleted=True)
        return context

def ajax_add_lock(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    item_id = request.POST.get('item_id')
    if item_id == "-1":
        count = Lock.objects.filter(name=name).exclude(b_deleted=True).count()
    else:
        count = Lock.objects.filter(name=name).exclude(b_deleted=True).exclude(id=item_id).count()
    if count == 0:
        if item_id == "-1":
            item = Lock(name=name, description=description)
            item.save()
        else:
            item = Lock.objects.get(id=item_id)
            item.name = name
            item.description = description
            item.save()

    items = Lock.objects.exclude(b_deleted=True)
    return render(request, 'settings/ajax_add_lock.html', {'items': items})
 
def ajax_delete_lock(request):
    item_id = request.POST.get('item_id')
    item = Lock.objects.get(id=item_id)
    item.b_deleted = True
    item.save()
    return JsonResponse({'status': 'ok'})

#############################################
########## Locks 
#############################################

@method_decorator(login_required, name='dispatch')
class Tasks(TemplateView):
    model = Task
    template_name = "settings/task.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Task.objects.exclude(b_deleted=True)
        return context

def ajax_add_task(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    item_id = request.POST.get('item_id')
    if item_id == "-1":
        count = Task.objects.filter(name=name).exclude(b_deleted=True).count()
    else:
        count = Task.objects.filter(name=name).exclude(b_deleted=True).exclude(id=item_id).count()
    if count == 0:
        if item_id == "-1":
            item = Task(name=name, description=description)
            item.save()
        else:
            item = Task.objects.get(id=item_id)
            item.name = name
            item.description = description
            item.save()

    items = Task.objects.exclude(b_deleted=True)
    return render(request, 'settings/ajax_add_task.html', {'items': items})
 
def ajax_delete_task(request):
    item_id = request.POST.get('item_id')
    item = Task.objects.get(id=item_id)
    item.b_deleted = True
    item.save()
    return JsonResponse({'status': 'ok'})
#############################################
########## Drawer's Color 
#############################################

@method_decorator(login_required, name='dispatch')
class Drawers(TemplateView):
    model = DrawerColor
    template_name = "settings/drawer_color.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = DrawerColor.objects.exclude(b_deleted=True)
        return context

def ajax_add_drawer(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    item_id = request.POST.get('item_id')
    if item_id == "-1":
        count = DrawerColor.objects.filter(name=name).exclude(b_deleted=True).count()
    else:
        count = DrawerColor.objects.filter(name=name).exclude(b_deleted=True).exclude(id=item_id).count()
    if count == 0:
        if item_id == "-1":
            item = DrawerColor(name=name, description=description)
            item.save()
        else:
            item = DrawerColor.objects.get(id=item_id)
            item.name = name
            item.description = description
            item.save()

    items = DrawerColor.objects.exclude(b_deleted=True)
    return render(request, 'settings/ajax_add_drawer.html', {'items': items})
 
def ajax_delete_drawer(request):
    item_id = request.POST.get('item_id')
    item = DrawerColor.objects.get(id=item_id)
    item.b_deleted = True
    item.save()
    return JsonResponse({'status': 'ok'})

#############################################
########## Strip's Color 
#############################################

@method_decorator(login_required, name='dispatch')
class Strips(TemplateView):
    model = Strip
    template_name = "settings/strip.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Strip.objects.exclude(b_deleted=True)
        return context

def ajax_add_strip(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    item_id = request.POST.get('item_id')
    if item_id == "-1":
        count = Strip.objects.filter(name=name).exclude(b_deleted=True).count()
    else:
        count = Strip.objects.filter(name=name).exclude(b_deleted=True).exclude(id=item_id).count()
    if count == 0:
        if item_id == "-1":
            item = Strip(name=name, description=description)
            item.save()
        else:
            item = Strip.objects.get(id=item_id)
            item.name = name
            item.description = description
            item.save()

    items = Strip.objects.exclude(b_deleted=True)
    return render(request, 'settings/ajax_add_strip.html', {'items': items})
 
def ajax_delete_strip(request):
    item_id = request.POST.get('item_id')
    item = Strip.objects.get(id=item_id)
    item.b_deleted = True
    item.save()
    return JsonResponse({'status': 'ok'})
#############################################
########## Location 
#############################################

@method_decorator(login_required, name='dispatch')
class Locations(TemplateView):
    model = Location
    template_name = "settings/location.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Location.objects.exclude(b_deleted=True)
        return context

def ajax_add_location(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    item_id = request.POST.get('item_id')
    if item_id == "-1":
        count = Location.objects.filter(name=name).exclude(b_deleted=True).count()
    else:
        count = Location.objects.filter(name=name).exclude(b_deleted=True).exclude(id=item_id).count()
    if count == 0:
        if item_id == "-1":
            item = Location(name=name, description=description)
            item.save()
        else:
            item = Location.objects.get(id=item_id)
            item.name = name
            item.description = description
            item.save()

    items = Location.objects.exclude(b_deleted=True)
    return render(request, 'settings/ajax_add_location.html', {'items': items})
 
def ajax_delete_location(request):
    item_id = request.POST.get('item_id')
    item = Location.objects.get(id=item_id)
    item.b_deleted = True
    item.save()
    return JsonResponse({'status': 'ok'})
# groups
@method_decorator(login_required, name='dispatch')
class Groups(TemplateView):
    model = Stock
    template_name = "groups/groups.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        # raw_query # yangyang
        filtered_ids = Stock.objects.filter(b_group=1).values_list('id', flat=True)
        max_query = "SELECT id, MAX(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity FROM backend_command WHERE finished=3 group by group_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        max_stock = Stock.objects.raw(max_query)
        for m in max_stock:
            max_quantity = m.quantity
        # raw_query # yangyang
        min_query = "SELECT id, MIN(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity FROM backend_command WHERE finished=3 group by group_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        min_stock = Stock.objects.raw(min_query)
        for m in min_stock:
            min_quantity = m.quantity

        context["min_quantity"] = min_quantity
        context["max_quantity"] = max_quantity
        context["sel_min_quantity"] = min_quantity
        context["sel_max_quantity"] = max_quantity
        context["sel_categories"] = []
        context["favorites"] = GroupFavorite.objects.filter(user=self.request.user)
        return context

@method_decorator(login_required, name='dispatch')
class GroupDetail(TemplateView):
    model = Stock
    template_name = "groups/group_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = Stock.objects.get(pk=self.kwargs.get('pk'))
        context["stocks"] = Stock.objects.filter().exclude(pk=self.kwargs.get('pk'))
        context["group_items"] = GroupItem.objects.filter(parent_id=self.kwargs.get('pk'))
        return context
@method_decorator(login_required, name='dispatch')
class GroupAdd(CreateView):
    model = Stock
    form_class = StockForm
    template_name = "groups/group_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter()
        context["locations"] = Location.objects.exclude(b_deleted=True)
        return context
    def get_success_url(self):
        return reverse('groups')

@method_decorator(login_required, name='dispatch')
class GroupUpdate(UpdateView):
    model = Stock
    form_class = StockForm
    template_name = "groups/group_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter()
        context["locations"] = Location.objects.exclude(b_deleted=True)
        stock = Stock.objects.get(pk=self.kwargs.get('pk'))
        context['stock'] = stock
        return context
    def get_success_url(self):
        stock = Stock.objects.get(pk=self.kwargs.get('pk'))
        exist = self.request.POST.get('exist')
        exist_pdf = self.request.POST.get('exist_pdf')
        if exist == 'NO':
            stock.picture= ''
        if exist_pdf == 'NO':
            stock.pdf = ''
        stock.save()
        return reverse('detail-group', kwargs={'pk': self.kwargs.get('pk')})

def ajax_list_groups(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    
    less = request.POST.get('less')
    greater = request.POST.get('greater')

    preview_query = Stock.objects.filter(b_group=1).filter(Q(name__icontains=search_key) | Q(reference__icontains=search_key))
    if selected_category != "":
        preview_query = preview_query.filter(category_id__in=selected_category.split(','))

    filtered_ids = preview_query.values_list('id', flat=True)
    
    where_qs = " and quantity>=" + str(from_package) + " and quantity<=" + str(to_package) + ""
    if less == "true":
        where_qs = where_qs + " and quantity < minium "
    if greater == "true":
        where_qs = where_qs + " and quantity >= minium "
    # raw_query # yangyang
    str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium FROM (\
            SELECT id, quantity, minium from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity, 0 as minium FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity, 0 as minium FROM backend_command WHERE finished=3 group by group_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity, 0 as minium FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ")" + where_qs
    
    stocks = Stock.objects.raw(str_query)
    
    paginator = Paginator(stocks, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'groups/ajax_group_list.html', {'stocks': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_groups(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')

    less = request.POST.get('less')
    greater = request.POST.get('greater')
    
    preview_query = Stock.objects.filter(b_group=1).filter(Q(name__icontains=search_key) | Q(reference__icontains=search_key))
    if selected_category != "":
        preview_query = preview_query.filter(category_id__in=selected_category.split(','))

    filtered_ids = preview_query.values_list('id', flat=True)
    
    where_qs = " and quantity>=" + str(from_package) + " and quantity<=" + str(to_package) + ""
    if less == "true":
        where_qs = where_qs + " and quantity < minium "
    if greater == "true":
        where_qs = where_qs + " and quantity >= minium "
    # raw_query # yangyang
    str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium FROM (\
            SELECT id, quantity, minium from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity, 0 as minium FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity, 0 as minium FROM backend_command WHERE finished=3 group by group_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity, 0 as minium FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ")" + where_qs
    
    stocks = Stock.objects.raw(str_query)
    
    paginator = Paginator(stocks, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'groups/ajax_group_grid.html', {'stocks': page_obj, 'page_obj': page_obj, 'paginator': paginator})
def ajax_delete_groups(request):
    checked_stocks = request.POST.get('checked_stocks')
    Stock.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_import_groups(request):
    
    if request.method == 'POST':
        org_column_names = ["Ref", "Name", "Quantity", "Minium", "Location", "Width", "Height", "Depth", "Weight", "Category"]
        filename = str(request.FILES['file'])
        existCSV = CsvArchivo.objects.all().count()
        if(existCSV > 0):
            CsvArchivo.objects.get().delete()
        obj = CsvArchivo(
            name = request.FILES['file'],
            file = request.FILES.get('file')
            )
        obj.save()
        current_csv = CsvArchivo.objects.get()
        path_csv = current_csv.file.url
            
        from django.conf import settings
        import urllib.request
        full_url = "http://"+request.META['HTTP_HOST'] + str(path_csv)
        print(full_url, "##########")
        path = "temp.csv"
            
        response = urllib.request.urlretrieve(full_url)
        contents = open(response[0]).read()
        
        f = open(path,'w')
        f.write(contents)
        f.close()

        df = pd.read_csv(path)    
        df.fillna("", inplace=True)
        column_names = list(df)
        dif_len = len(list(set(org_column_names) - set(column_names)))

        if dif_len == 0:
            record_count = len(df.index)
            success_record = 0
            failed_record = 0
            exist_record = 0
            for index, row in df.iterrows():
                
                try:
                    cate_instance = Category.objects.get(name=row["Category"])
                    loc_instance = Location.objects.get(name=row["Location"])
                except Exception as e:
                    print(e)
                    failed_record += 1
                    continue
                exist_count = Stock.objects.filter(reference=row["Ref"]).count()
                if exist_count == 0:
                    stock = Stock(
                        name=row["Name"], 
                        reference=row["Ref"], 
                        quantity=row["Quantity"], 
                        category=cate_instance, 
                        location=loc_instance,
                        minium=row["Minium"],
                        width=row["Width"],
                        height=row["Height"],
                        depth=row["Depth"],
                        weight=row["Weight"], 
                        user=request.user,
                        b_group=True,
                    )
                    stock.save()
                    success_record += 1
                else:
                    stock = Stock.objects.get(reference=row["Ref"])
                    stock.name = row["Name"]
                    stock.quantity = row["Quantity"]
                    stock.location = loc_instance
                    stock.minium = row["Minium"]
                    stock.width = row["Width"]
                    stock.height = row["Height"]
                    stock.depth = row["Depth"]
                    stock.weight = row["Weight"]
                    stock.category = cate_instance
                    stock.user = request.user
                    b_group = True
                    stock.save()
                    exist_record += 1
            os.remove(path)
            return JsonResponse({'status':'true','error_code':'0', 'total': record_count, 'success': success_record, 'failed': failed_record, 'exist': exist_record})
        else:
            os.remove(path)
            # column count is not equals
            return JsonResponse({'status':'false','error_code':'1'})
    return HttpResponse("Ok")

def ajax_export_groups(request):
    resource = GroupResource()
    dataset = resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="groups.csv"'
    return response

@method_decorator(login_required, name='dispatch')
class GroupsFavorite(TemplateView):
    model = Stock
    template_name = "groups/groups.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        # raw_query # yangyang
        filtered_ids = Stock.objects.filter(b_group=1).values_list('id', flat=True)
        max_query = "SELECT id, MAX(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity FROM backend_command WHERE finished=3 group by group_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        max_stock = Stock.objects.raw(max_query)
        for m in max_stock:
            max_quantity = m.quantity
        # raw_query # yangyang
        min_query = "SELECT id, MIN(quantity) as quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity FROM backend_command WHERE finished=3 group by group_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) WHERE id in (" + ','.join(map(str, filtered_ids)) + ") GROUP BY id)" 
        
        min_stock = Stock.objects.raw(min_query)
        for m in min_stock:
            min_quantity = m.quantity
        context["min_quantity"] = min_quantity
        context["max_quantity"] = max_quantity
        favor = GroupFavorite.objects.get(id=self.kwargs.get('pk'))
        context["sel_min_quantity"] = favor.min_quantity
        context["sel_max_quantity"] = favor.max_quantity
        context["sel_categories"] = favor.category.split(',')
        context["sel_less"] = favor.less
        context["sel_greater"] = favor.greater

        context["favorites"] = GroupFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_favorite_groups(request):
    selected_category = request.POST.get('selected_category')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    less = request.POST.get('less')
    greater = request.POST.get('greater')
    name = request.POST.get('name')

    count = GroupFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = GroupFavorite.objects.filter(category=selected_category, min_quantity=from_package, max_quantity=to_package, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            stock = GroupFavorite(name=name, category=selected_category, min_quantity=from_package, max_quantity=to_package, user=request.user, less=less, greater=greater)
            stock.save()

            favorites = GroupFavorite.objects.filter(user=request.user)
            return render(request, 'groups/ajax_favor_groups.html', {'favorites': favorites})

def ajax_delete_group_favorite(request):
    del_id = request.POST.get('id')
    GroupFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})
# group item
def ajax_add_group_item(request):
    stock_id = request.POST.get('stock_id')
    quantity = request.POST.get('quantity')
    item_id = request.POST.get('add_id')
    group_id = request.POST.get('group_id')

    if item_id == "-1":
        count = GroupItem.objects.filter(stock_id=stock_id, parent_id=group_id).count()
    else:
        count = GroupItem.objects.filter(stock_id=stock_id, parent_id=group_id).exclude(id=item_id).count()

    if count == 0:
        if item_id == "-1":
            cate = GroupItem(stock_id=stock_id, quantity=quantity, parent_id=group_id)
            cate.save()
        else:
            cate = GroupItem.objects.get(id=item_id)
            cate.parent.id = group_id
            cate.stock.id = stock_id
            cate.quantity = quantity
            cate.save()

    items = GroupItem.objects.filter(parent_id=group_id)

    paginator = Paginator(items, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'groups/ajax_group_item_list.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_group_item(request):
    group_id = request.POST.get('group_id')
    
    items = GroupItem.objects.filter(parent_id=group_id)
    
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'groups/ajax_group_item_grid.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_list_group_item(request):
    group_id = request.POST.get('group_id')
    
    items = GroupItem.objects.filter(parent_id=group_id)
    
    paginator = Paginator(items, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'groups/ajax_group_item_list.html', {'items': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_delete_group_items(request):
    checked_stocks = request.POST.get('checked_stocks')
    GroupItem.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

# Commands
@method_decorator(login_required, name='dispatch')
class Commands(TemplateView):
    model = Command
    template_name = "commands/commands.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        min_quantity = Command.objects.all().aggregate(Min('quantity'))["quantity__min"]
        max_quantity = Command.objects.all().aggregate(Max('quantity'))["quantity__max"]

        context["min_quantity"] = min_quantity if min_quantity != None else 0
        context["max_quantity"] = max_quantity if max_quantity != None else 0
        context["categories"] = Category.objects.all()
        
        today = date.today()
        start_date = Command.objects.all().aggregate(Min('date'))["date__min"]
        context["start_date"] = today if start_date == None else start_date 
        end_date = Command.objects.all().aggregate(Max('date'))["date__max"]
        context["end_date"] = today if end_date == None else end_date

        context["workers"] = Command.objects.values('worker').distinct().order_by()

        context["sel_min_quantity"] = min_quantity if min_quantity != None else 0
        context["sel_max_quantity"] = max_quantity if max_quantity != None else 0
        context["sel_categories"] = []
        context["sel_workers"] = []
        
        context["favorites"] = CommandFavorite.objects.filter(user=self.request.user)
        return context

@method_decorator(login_required, name='dispatch')
class CommandAdd(CreateView):
    model = Command
    form_class = CommandForm
    template_name = "commands/command_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = Stock.objects.filter(b_group=1)
        return context
    def get_success_url(self):
        return reverse('commands')

@method_decorator(login_required, name='dispatch')
class CommandDetail(TemplateView):
    model = Command
    template_name = "commands/command_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        command = Command.objects.get(pk=self.kwargs.get('pk'))
        context['command'] = command

        context['items'] = GroupItem.objects.filter(parent_id=command.group_id)
        context["workhistory"] = CommandWorkerHistory.objects.filter(command_id=command.id)
        if command.finished == 3:
            count = CommandWorkerHistory.objects.filter(command_id=command.id).count()
            if count != 0:
                break_duration = CommandWorkerHistory.objects.annotate(
                    diff=ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
                ).filter(command_id=command.id).aggregate(Sum('diff'))["diff__sum"]
            else:
                break_duration = 0
            working_duration = Command.objects.annotate(
                diff=ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
            ).filter(id=command.id).aggregate(Sum('diff'))["diff__sum"]

            context["break_duration"] = break_duration
            if count != 0:
                context["working_duration"] = working_duration - break_duration
            else:
                context["working_duration"] = working_duration
        else:
            context["break_duration"] = ""
            context["working_duration"] = ""
            
        return context
    def get_success_url(self):
        return reverse('commands')

@method_decorator(login_required, name='dispatch')
class CommandUpdate(UpdateView):
    model = Command
    form_class = CommandForm
    template_name = "commands/command_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = Stock.objects.filter(b_group=1)
        command = Command.objects.get(pk=self.kwargs.get('pk'))
        context['command'] = command
        return context
    def get_success_url(self):
        return reverse('detail-command', kwargs={'pk': self.kwargs.get('pk')})
def ajax_command_new_detail(request):
    group_id = request.POST.get('group_id')
    quantity = request.POST.get('quantity')
    comm_id = request.POST.get('comm_id')

    stock = Stock.objects.get(id=group_id)
    str_query = "SELECT id, quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
        SELECT id, quantity from backend_stock WHERE id=" + str(stock.id) + "\
        UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id WHERE I.stock_id="+ str(stock.id) +" group by I.stock_id \
        UNION ALL SELECT group_id as id, SUM(quantity) as quantity FROM backend_command WHERE finished=3 and group_id="+ str(stock.id) +" group by group_id\
        UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' and OI.stock_id='"+str(stock.id)+"' group by OI.stock_id\
            ) GROUP BY id)"
    tmp = Stock.objects.raw(str_query)
    
    for temp in tmp:
        stock.quantity = temp.quantity

    items = GroupItem.objects.filter(parent_id=group_id)

    where_qs = ""
    if str(comm_id) != "-1":
        where_qs = " and C.id <> " + str(comm_id)
    for item in items:
        # raw_query # yangyang
        str_query = "SELECT id, quantity FROM (SELECT id, SUM(quantity) as quantity FROM (\
            SELECT id, quantity from backend_stock WHERE id=" + str(item.stock.id) + "\
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id WHERE I.stock_id="+ str(item.stock.id) + where_qs +" group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity FROM backend_command WHERE finished=3 and group_id="+ str(item.stock.id) +" group by group_id\
            UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id WHERE P.stock_id="+str(item.stock.id)+" group by P.stock_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' and OI.stock_id='"+str(item.stock.id)+"' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id)"
        tmp = Stock.objects.raw(str_query)
        item.current_quantity = 0
        for temp in tmp:
            item.current_quantity = temp.quantity
    return render(request, 'commands/ajax_command_new_detail.html', {'stock': stock, 'items': items, 'quantity': quantity})

def ajax_list_commands(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    selected_worker = request.POST.get('selected_work')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    
    in_progress = request.POST.get('in_progress')
    finished = request.POST.get('finished')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    preview_query = Command.objects.filter(Q(group__name=search_key) | Q(group__reference__icontains=search_key), quantity__gte=from_package, quantity__lte=to_package).filter(date__range=[start_date, end_date])
    if in_progress == "true":
        preview_query = preview_query.exclude(finished=3).order_by('-date')
    elif finished == "true":
        preview_query = preview_query.filter(finished=3).order_by('-date')

    if selected_category != "":
        preview_query = preview_query.filter(group__category__id__in=selected_category.split(','))
    
    if selected_worker != "":
        preview_query = preview_query.filter(worker__in=selected_worker.split(','))
    
    commands = preview_query.order_by("-date")    
    
    paginator = Paginator(commands, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'commands/ajax_command_list.html', {'commands': page_obj, 'page_obj': page_obj, 'paginator': paginator})

def ajax_grid_commands(request):
    search_key = request.POST.get('search_key')
    selected_category = request.POST.get('selected_category')
    selected_worker = request.POST.get('selected_work')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    
    in_progress = request.POST.get('in_progress')
    finished = request.POST.get('finished')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    preview_query = Command.objects.filter(Q(group__name=search_key) | Q(group__reference__icontains=search_key), quantity__gte=from_package, quantity__lte=to_package).filter(date__range=[start_date, end_date])
    if in_progress == "true":
        preview_query = preview_query.filter(finished=1).order_by('-date')
    elif finished == "true":
        preview_query = preview_query.filter(finished=3).order_by('-date')

    if selected_category != "":
        preview_query = preview_query.filter(group__category__id__in=selected_category.split(','))
    
    if selected_worker != "":
        preview_query = preview_query.filter(worker__in=selected_worker.split(','))
    
    commands = preview_query.order_by("-date") 
    
    paginator = Paginator(commands, 24)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'commands/ajax_command_grid.html', {'commands': page_obj, 'page_obj': page_obj, 'paginator': paginator})
def ajax_delete_commands(request):
    checked_stocks = request.POST.get('checked_stocks')
    Command.objects.filter(id__in=checked_stocks.split(',')).delete()
    
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class CommandsFavorite(TemplateView):
    model = Command
    template_name = "commands/commands.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        min_quantity = Command.objects.all().aggregate(Min('quantity'))["quantity__min"]
        max_quantity = Command.objects.all().aggregate(Max('quantity'))["quantity__max"]
        context["min_quantity"] = min_quantity
        context["max_quantity"] = max_quantity
        context["categories"] = Category.objects.all()
        context["workers"] = Command.objects.values('worker').distinct()
        
        favor = CommandFavorite.objects.get(id=self.kwargs.get('pk'))

        context["sel_min_quantity"] = favor.min_quantity
        context["sel_max_quantity"] = favor.max_quantity
        context["sel_categories"] = favor.category.split(',')
        context["sel_workers"] = favor.worker.split(',')
        context["in_progress"] = favor.in_progress
        context["finished"] = favor.finished
        context["start_date"] = favor.start_date
        context["end_date"] = favor.end_date
        
        context["favorites"] = CommandFavorite.objects.filter(user=self.request.user)
        return context

def ajax_add_favorite_commands(request):
    selected_category = request.POST.get('selected_category')
    selected_worker = request.POST.get('selected_work')
    from_package = request.POST.get('from_package')
    to_package = request.POST.get('to_package')
    
    in_progress = request.POST.get('in_progress')
    finished = request.POST.get('finished')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    name = request.POST.get('name')

    count = CommandFavorite.objects.filter(name=name, user=request.user).count()
    if count != 0:
        return JsonResponse({'err_code': '1'})
    else:
        count1 = CommandFavorite.objects.filter(category=selected_category, min_quantity=from_package, max_quantity=to_package, start_date=start_date, end_date=end_date, worker=selected_worker, user=request.user).count()
        if count1 != 0:
            return JsonResponse({'err_code': '2'})
        else:
            stock = CommandFavorite(name=name, category=selected_category, min_quantity=from_package, max_quantity=to_package, start_date=start_date, end_date=end_date, worker=selected_worker, in_progress=in_progress, finished=finished, user=request.user)
            stock.save()

            favorites = CommandFavorite.objects.filter(user=request.user)
            return render(request, 'commands/ajax_favor_commands.html', {'favorites': favorites})

def ajax_delete_command_favorite(request):
    del_id = request.POST.get('id')
    CommandFavorite.objects.filter(id=del_id).delete()
    
    return JsonResponse({'status': 'ok'})

def ajax_command_record_datetime(request):
    comm_id = request.POST.get('comm_id')
    status = request.POST.get('status')
    description = request.POST.get('description')
    current_datetime = request.POST.get('current_datetime')

    print(current_datetime, status)
    command = Command.objects.get(id=comm_id)
    if status == "0":
        command.start = current_datetime
        command.finished = 1
        command.save()
        return JsonResponse({'err_code': '1', 'start_time': current_datetime})
    elif status == "1":
        workerhistory = CommandWorkerHistory(command_id=comm_id, start=current_datetime, description=description)
        workerhistory.save()
        command.finished = 2
        command.save()
    elif status == "2":
        workerhistory = CommandWorkerHistory.objects.filter(command_id=comm_id).latest('id')
        workerhistory.end = current_datetime
        workerhistory.save()
        command.finished = 1
        command.save()
    elif status == "3":
        count = CommandWorkerHistory.objects.filter(command_id=comm_id).count()
        if count != 0:
            workerhistory = CommandWorkerHistory.objects.filter(command_id=comm_id).latest('id')
            if workerhistory.end == None:
                workerhistory.end = current_datetime
                workerhistory.save()
        command.end = current_datetime
        command.finished = 3
        command.save()
        if count != 0:
            break_duration = CommandWorkerHistory.objects.annotate(
                    diff=ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
                ).filter(command_id=comm_id).aggregate(Sum('diff'))["diff__sum"]
        else:
            break_duration = 0
        working_duration = Command.objects.annotate(
            diff=ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
        ).filter(id=comm_id).aggregate(Sum('diff'))["diff__sum"]
        
        return JsonResponse({'err_code': '3', 'end_time': current_datetime, 'working_duration': str(working_duration), 'break_duration': str(break_duration)})
    
    workhistory = CommandWorkerHistory.objects.filter(command_id=comm_id)
    return render(request, 'commands/ajax_command_work_history.html', {'workhistory': workhistory})

@method_decorator(login_required, name='dispatch')
class Mailings(TemplateView):
    model = Mailing
    template_name = "mail/mail_marketing.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        mailing = Mailing.objects.all()
        try:
            for ma in mailing:
                maillist = ma.mail_list
                if maillist != None:
                    maillist_array = []
                    for i in range(len(maillist.split(",")) -1):
                        mail_temp = MailList.objects.filter(pk=int(maillist.split(",")[i]))
                        if mail_temp.exists():
                            mail = MailList.objects.get(pk=int(maillist.split(",")[i]))
                            maillist_array.append(mail.name)
                    separator = ', '
                    temp = separator.join(maillist_array)
                    ma.mailing_list = temp
        except:
            pass

        context["mailings"] = mailing

        return context

@method_decorator(login_required, name='dispatch')
class MailListing(TemplateView):
    model = MailList
    template_name = "mail/mail_list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lists"] = MailList.objects.all()
        
        return context

def ajax_add_maillist(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    list_id = request.POST.get('list_id')

    if list_id == "-1":
        count = MailList.objects.filter(name=name).count()
    else:
        count = MailList.objects.filter(name=name).exclude(id=list_id).count()
    if count == 0:
        if list_id == "-1":
            list_v = MailList(name=name, description=description)
            list_v.save()
        else:
            list_v = MailList.objects.get(id=list_id)
            list_v.name = name
            list_v.description = description
            list_v.save()

    return HttpResponse("Ok")

def ajax_delete_lists(request):
    
    list_id = request.POST.get('list_id')
    list_v = MailList.objects.get(id=list_id)
    list_v.delete()
    remove_key = str(list_id) + ","

    contacts = Client.objects.filter(mail_list__contains=remove_key)
    for contact in contacts:
        mail_list_val = contact.mail_list
        mail_list_change = mail_list_val.replace(remove_key, '')
        contact.mail_list = mail_list_change
        contact.save()

    return JsonResponse({'status': 'ok'})

class MailingDetail(TemplateView):
    model = Mailing
    template_name = "mail/mailing_detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = Mailing.objects.get(pk=self.kwargs.get('pk'))
        maillists = mailing.mail_list
        if maillists != None:
            maillists_array = []
            for i in range(len(maillists.split(",")) -1):
                mail_v = MailList.objects.filter(pk=int(maillists.split(",")[i]))
                if mail_v.exists():
                    mailtemp = MailList.objects.get(pk=int(maillists.split(",")[i]))
                    maillists_array.append(mailtemp.name)
            separator = ', '
            temp = separator.join(maillists_array)
            mailing.maillists = temp
        context['mailing'] = mailing

        return context

@method_decorator(login_required, name='dispatch')
class MailingAdd(CreateView):
    model = User
    form_class = MailingForm
    template_name = "mail/mailing_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maillists'] = MailList.objects.all().order_by('name')
        context["sel_mailings"] = []
        context["sel_mail"] = self.kwargs.get('pk')
        return context
    def get_success_url(self):
        mail_list = self.request.POST.getlist('maillists')
        if len(mail_list) > 0:
            separator = ', '
            temp = separator.join(mail_list) + ","
            
            mailing = Mailing.objects.get(pk=self.object.pk)
            mailing.mail_list = temp
            mailing.save()
            
        return reverse('mailings')

def ajax_delete_mailings(request):
    
    mail_id = request.POST.get('mail_id')
    mail = Mailing.objects.get(id=mail_id)
    mail.delete()
    return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class MailingUpdate(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mail/mailing_new.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = Mailing.objects.get(pk=self.kwargs.get('pk'))
        context['mailing'] = mailing
        context['maillists'] = MailList.objects.all().order_by('name')
        if mailing.mail_list != None:
            submail = mailing.mail_list.split(",")
            submail_arr = []
            for i in range(len(submail) - 1):
                submail_arr.append(submail[i].strip())
            context["sel_mailings"] = submail_arr
        else:
            context["sel_mailings"] = []
        return context
    def get_success_url(self):
        mailing = Mailing.objects.get(pk=self.kwargs.get('pk'))

        mail_list = self.request.POST.getlist('maillists')
        if len(mail_list) > 0:
            separator = ', '
            temp = separator.join(mail_list) + ","
            
            mailing = Mailing.objects.get(pk=self.object.pk)
            mailing.mail_list = temp
            mailing.save()
        
        return reverse('mailings-detail', kwargs={'pk': self.kwargs.get('pk')})

def ajax_mail_list(request):
    my_id = request.POST.get("lead_list_id")
    search_key = str(my_id) + ","
    contacts = Client.objects.filter(mail_list__contains=search_key).filter(parent=None)

    paginator = Paginator(contacts, 10)
    page_number = request.POST.get('page')
    page_obj = paginator.get_page(page_number)

    for obj in page_obj:
        obj.childs = Client.objects.filter(parent_id=obj.id)

    return render(request, 'mail/ajax-mail-list-detail.html', {'contacts': page_obj, 'page_obj': page_obj, 'paginator': paginator})


class MailListDetail(TemplateView):
    model = Client
    template_name = "mail/mail_list_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_id = self.kwargs.get('pk')
        search_key = str(my_id) + ","
        contacts = Client.objects.filter(mail_list__contains=search_key).filter(parent=None)

        paginator = Paginator(contacts, 10)
        page_number = self.request.POST.get('page')
        page_obj = paginator.get_page(page_number)

        for obj in page_obj:
            obj.childs = Client.objects.filter(parent_id=obj.id)

        print("====================", page_obj)

        context['contacts'] = page_obj
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        return context
    
