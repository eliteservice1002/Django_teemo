from django.db import models
from django.contrib.auth.models import AbstractUser

from cities_light.models import Country
import os
import datetime
from django.utils.timesince import timesince
# Create your models here.

def content_file_user(instance, filename):
    return 'profile/{1}'.format(instance, filename)

def content_file_stock(instance, filename):
    return 'stock/{1}'.format(instance, filename)

def content_file_box(instance, filename):
    return 'box/{1}'.format(instance, filename)

def content_file_stock_pdf(instance, filename):
    return 'contact/pdf/{1}'.format(instance, filename)

def content_file_contact(instance, filename):
    return 'contact/{1}'.format(instance, filename)

def content_file_contact_pdf(instance, filename):
    return 'contact/pdf/{1}'.format(instance, filename)
def csv_file(instance, filename):
    return 'csv/file/{1}'.format(instance, filename)

def content_file_chatter(instance, filename):
    return 'chatter/{1}'.format(instance, filename)

class UserRole(models.Model):
    supplier_add = models.BooleanField(default=False)
    supplier_up = models.BooleanField(default=False)
    supplier_del = models.BooleanField(default=False)
    lead_add = models.BooleanField(default=False)
    lead_up = models.BooleanField(default=False)
    lead_del = models.BooleanField(default=False)
    mail_add = models.BooleanField(default=False)
    mail_up = models.BooleanField(default=False)
    mail_del = models.BooleanField(default=False)
    product_add = models.BooleanField(default=False)
    product_up = models.BooleanField(default=False)
    product_del = models.BooleanField(default=False)
    purchase_add = models.BooleanField(default=False)
    purchase_up = models.BooleanField(default=False)
    purchase_del = models.BooleanField(default=False)
    transport_add = models.BooleanField(default=False)
    transport_up = models.BooleanField(default=False)
    transport_del = models.BooleanField(default=False)
    manufact_add = models.BooleanField(default=False)
    manufact_up = models.BooleanField(default=False)
    manufact_del = models.BooleanField(default=False)
    outcome_add = models.BooleanField(default=False)
    outcome_up = models.BooleanField(default=False)
    outcome_del = models.BooleanField(default=False)
    trolley_add = models.BooleanField(default=False)
    trolley_up = models.BooleanField(default=False)
    trolley_del = models.BooleanField(default=False)
    invent_add = models.BooleanField(default=False)
    invent_up = models.BooleanField(default=False)
    invent_del = models.BooleanField(default=False)
    offer_add = models.BooleanField(default=False)
    offer_up = models.BooleanField(default=False)
    offer_del = models.BooleanField(default=False)
    time_add = models.BooleanField(default=False)
    time_up = models.BooleanField(default=False)
    time_del = models.BooleanField(default=False)
    setting_add = models.BooleanField(default=False)
    setting_up = models.BooleanField(default=False)
    setting_del = models.BooleanField(default=False)



class User(AbstractUser):
    picture = models.ImageField(upload_to=content_file_user, blank=True)
    telephone = models.IntegerField(blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    role = models.ForeignKey('UserRole', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.username
    class Meta:
        permissions = (("admin_user","Can use modules admin"),("guest_user","Can use modules guest"))

class CsvArchivo(models.Model):
    name = models.CharField(max_length=155, null=True, blank=True)
    file = models.FileField(upload_to=csv_file, blank=True, null=True)

class Category(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class WallType(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    b_deleted = models.BooleanField(null=True, blank=True, default=False)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Castor(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    b_deleted = models.BooleanField(null=True, blank=True, default=False)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Color(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    b_deleted = models.BooleanField(null=True, blank=True, default=False)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class DrawerColor(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    b_deleted = models.BooleanField(null=True, blank=True, default=False)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Location(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    b_deleted = models.BooleanField(null=True, blank=True, default=False)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Strip(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    b_deleted = models.BooleanField(null=True, blank=True, default=False)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Lock(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    b_deleted = models.BooleanField(null=True, blank=True, default=False)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Task(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    b_deleted = models.BooleanField(null=True, blank=True, default=False)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Tax(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Stock(models.Model):
    name = models.CharField(max_length=150)
    picture = models.ImageField(upload_to=content_file_stock, blank=True)
    reference = models.TextField(unique=True, blank=True)
    #internal = models.TextField(unique=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(null=True, blank=True, default=1)
    minium = models.IntegerField(null=True, blank=True, default=1)
    b_group = models.IntegerField(null=True, blank=True, default=0)
    # 0 : stocks, 1: groups(products), 2: boxs
    pdf = models.FileField(upload_to=content_file_stock_pdf, blank=True)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, blank=True, null=True)
    width = models.IntegerField(null=True, blank=True, default=1)
    height = models.IntegerField(null=True, blank=True, default=1)
    depth = models.IntegerField(null=True, blank=True, default=1)
    weight = models.IntegerField(null=True, blank=True, default=1)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    sale_price = models.IntegerField(null=True, blank=True, default=1)
    tax = models.ForeignKey('Tax', on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return self.name
    def filename(self):
        return os.path.basename(self.pdf.name)
class StockFavorite(models.Model):
    name = models.CharField(max_length=150)
    category = models.TextField(blank=True)
    min_quantity = models.IntegerField(null=True, blank=True, default=1)
    max_quantity = models.IntegerField(null=True, blank=True, default=1)
    less = models.CharField(max_length=10, null=True, blank=True)
    greater = models.CharField(max_length=10, null=True, blank=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name


class BoxFavorite(models.Model):
    name = models.CharField(max_length=150)
    category = models.TextField(blank=True)
    min_quantity = models.IntegerField(null=True, blank=True, default=1)
    max_quantity = models.IntegerField(null=True, blank=True, default=1)
    less = models.CharField(max_length=10, null=True, blank=True)
    greater = models.CharField(max_length=10, null=True, blank=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class GroupFavorite(models.Model):
    name = models.CharField(max_length=150)
    category = models.TextField(blank=True)
    min_quantity = models.IntegerField(null=True, blank=True, default=1)
    max_quantity = models.IntegerField(null=True, blank=True, default=1)
    less = models.CharField(max_length=10, null=True, blank=True)
    greater = models.CharField(max_length=10, null=True, blank=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class GroupItem(models.Model):
    stock = models.ForeignKey('Stock', on_delete=models.SET_NULL, blank=True, null=True, related_name="stock_item")
    quantity = models.IntegerField(null=True, blank=True, default=1)
    parent = models.ForeignKey('Stock', on_delete=models.SET_NULL, blank=True, null=True, related_name="group")

    def __str__(self):
        return self.quantity

class Mailing(models.Model):
    name = models.CharField(max_length=500)
    content = models.TextField(max_length=400, blank=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    mail_list = models.CharField(blank=True, max_length=500, null=True)

    def __str__(self):
        return self.name

class MailList(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class SubProduct(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(max_length=400, blank=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(unique=True, max_length=150)
    nif = models.CharField(max_length=250, blank=True, null=True)
    picture = models.ImageField(upload_to=content_file_contact, blank=True)
    telephone = models.CharField(max_length=250, blank=True, null=True)
    mobile = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    web = models.CharField(max_length=250, blank=True, null=True)
    notes = models.TextField(blank=True)
    address = models.TextField(blank=True)
    pdf = models.FileField(upload_to=content_file_contact_pdf, blank=True)
    products = models.CharField(blank=True, max_length=150, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    #parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='children')
    
    def __str__(self):
        return self.name

    def filename(self):
        return os.path.basename(self.pdf.name)
    class Meta:
        ordering = ['-id']

class SubContact(models.Model):
    name = models.CharField(max_length=500)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=250, blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return self.name

class ContactFavorite(models.Model):
    name = models.CharField(max_length=150)
    country = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(unique=True, max_length=150)
    nif = models.CharField(max_length=250, blank=True, null=True)
    picture = models.ImageField(upload_to=content_file_contact, blank=True)
    telephone = models.CharField(max_length=250, blank=True, null=True)
    mobile = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    web = models.CharField(max_length=250, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    postalcode = models.CharField(max_length=250, blank=True, null=True)
    state = models.CharField(max_length=250, blank=True, null=True)
    notes = models.TextField(blank=True)
    pdf = models.FileField(upload_to=content_file_contact_pdf, blank=True)
    products = models.TextField(blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True)
    b_client = models.BooleanField(default=False)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='children')
    mail_list = models.CharField(blank=True, max_length=500, null=True)
    
    def __str__(self):
        return self.name

    def filename(self):
        return os.path.basename(self.pdf.name)

    class Meta:
        ordering = ['-id']
class ClientAddress(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, blank=True, null=True)
    address = models.TextField(blank=True)

class ClientChatter(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, blank=True, null=True)
    clientaddress = models.ForeignKey('ClientAddress', on_delete=models.CASCADE, blank=True, null=True)
    name = models.TextField(blank=True)
    flag = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    pdfname = models.CharField(max_length=255, blank=True, null=True)
    pdf = models.FileField(upload_to=content_file_chatter, blank=True)
    comment = models.TextField(blank=True)


class ClientFavorite(models.Model):
    name = models.CharField(max_length=150)
    country = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class Command(models.Model):
    name = models.CharField(max_length=150)
    date = models.DateField(blank=True, null=True)
    group = models.ForeignKey('Stock', on_delete=models.SET_NULL, blank=True, null=True, related_name='command')
    quantity = models.IntegerField(null=True, blank=True, default=1)
    worker = models.CharField(max_length=100, null=True, blank=True)
    finished = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now=True, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.name

class CommandFavorite(models.Model):
    name = models.CharField(max_length=150)
    category = models.TextField(blank=True)
    worker = models.TextField(blank=True)
    min_quantity = models.IntegerField(null=True, blank=True, default=1)
    max_quantity = models.IntegerField(null=True, blank=True, default=1)
    in_progress = models.CharField(max_length=10, null=True, blank=True)
    finished = models.CharField(max_length=10, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class CommandWorkerHistory(models.Model):
    command = models.ForeignKey('Command', on_delete=models.SET_NULL, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.description

    def get_time_diff(self):
        if self.end != None:
            dt = self.end - self.start
        else:
            dt = ""
        return dt

class ProviderAdd(models.Model):
    provider = models.ForeignKey('Contact', on_delete=models.SET_NULL, blank=True, null=True)
    reference = models.CharField(max_length=10, null=True, blank=True)
    price = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(blank=True)
    stock = models.ForeignKey('Stock', on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.provider


    
