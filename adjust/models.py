from django.db import models
import os
# Create your models here.
from backend.models import User, Client, Stock, WallType, Castor, Color, DrawerColor


class AdjustItem(models.Model):
    name = models.CharField(max_length=150)
    adjust_date = models.DateField(blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    current_qt = models.IntegerField(null=True, blank=True)
    adjust_qt = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']

class AdjustFavorite(models.Model):
    name = models.CharField(max_length=150)
    owner = models.TextField(blank=True)
    stock = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name