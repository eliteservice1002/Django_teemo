from django.db import models
import os
# Create your models here.
from backend.models import User, Client, Stock

class Outcome(models.Model):
    name = models.CharField(max_length=150)
    order_date = models.DateField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True)
    finished = models.BooleanField(blank=True, null=True, default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']

class OutcomeFavorite(models.Model):
    name = models.CharField(max_length=150)
    client = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class OutcomeItem(models.Model):
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    order_quantity = models.IntegerField(null=True, blank=True)
    order_date = models.DateField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.stock.name
    class Meta:
        ordering = ['-id']