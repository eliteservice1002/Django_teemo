from django.db import models
import os
# Create your models here.
from backend.models import User, Contact, Stock

class Purchase(models.Model):
    name = models.CharField(max_length=150)
    order_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']

class PurchaseFavorite(models.Model):
    name = models.CharField(max_length=150)
    supplier = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class OrderItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    order_quantity = models.IntegerField(null=True, blank=True)
    order_date = models.DateField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']

class OrderIncomeValid(models.Model):
    orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE, blank=True, null=True)
    income_quantity = models.IntegerField(null=True, blank=True)
    income_date = models.DateField(blank=True, null=True)
    income_description = models.TextField(blank=True)
    valid_quantity = models.IntegerField(null=True, blank=True)
    valid_date = models.DateField(blank=True, null=True)
    valid_description = models.TextField(blank=True)
    refund_flag = models.BooleanField(blank=True, default=False)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        ordering = ['income_date']

class Transport(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=150)
    departure = models.DateField(blank=True, null=True)
    arrival = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    container = models.IntegerField(null=True, blank=True, default=0)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

class TransportFavorite(models.Model):
    name = models.CharField(max_length=150)
    supplier = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    dep_start_date = models.DateField(blank=True, null=True)
    dep_end_date = models.DateField(blank=True, null=True)
    arr_start_date = models.DateField(blank=True, null=True)
    arr_end_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class DepatureItem(models.Model):
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']

class BrokenFavorite(models.Model):
    name = models.CharField(max_length=150)
    supplier = models.TextField(blank=True)
    stock = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class RefundHistory(models.Model):
    description = models.TextField(blank=True)
    supplier = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(null=True, blank=True)
    refund_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.description

class RefundFavorite(models.Model):
    name = models.CharField(max_length=150)
    supplier = models.TextField(blank=True)
    stock = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name