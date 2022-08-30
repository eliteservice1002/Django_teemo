from django.db import models
import os
# Create your models here.
from backend.models import User, Client, Stock, WallType, Castor, Color, DrawerColor, Strip, Lock

def content_file_trolley(instance, filename):
    return 'trolley/{1}'.format(instance, filename)

class TrolleyOrder(models.Model):
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

class TrolleyOrderFavorite(models.Model):
    name = models.CharField(max_length=150)
    client = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name

class TrolleyOrderItem(models.Model):
    position = models.IntegerField(null=True, blank=True, default=1)
    trolley = models.ForeignKey(TrolleyOrder, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    wall_type = models.ForeignKey(WallType, on_delete=models.SET_NULL, blank=True, null=True)
    castor = models.ForeignKey(Castor, on_delete=models.SET_NULL, blank=True, null=True, related_name='castor_stock')
    color_side = models.ForeignKey(Color, on_delete=models.SET_NULL, blank=True, null=True, related_name='color_drawer')
    color_drawer = models.ForeignKey(DrawerColor, on_delete=models.SET_NULL, blank=True, null=True)
    strip = models.ForeignKey(Strip, on_delete=models.SET_NULL, blank=True, null=True)
    lock = models.ForeignKey(Lock, on_delete=models.SET_NULL, blank=True, null=True)
    order_quantity = models.IntegerField(null=True, blank=True)
    configuration = models.TextField(blank=True)
    order_date = models.DateField(blank=True, null=True)
    manu_workers = models.TextField(blank=True)
    clean_worker = models.TextField(blank=True)
    check_worker = models.TextField(blank=True)
    finished = models.BooleanField(blank=True, null=True, default=False)
    finished_time = models.IntegerField(null=True, blank=True)
    check_description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.stock.name
    class Meta:
        ordering = ['id']

class AccesoriesItem(models.Model):
    trolley_item = models.ForeignKey(TrolleyOrderItem, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(null=True, blank=True, default=1)
    description = models.TextField(blank=True)
    direction = models.TextField(blank=True)
    packaging = models.TextField(blank=True)
    def __str__(self):
        return self.stock.name
    class Meta:
        ordering = ['id']

class FinalPhotos(models.Model):
	trolley_item = models.ForeignKey(TrolleyOrderItem, on_delete=models.CASCADE, blank=True, null=True)
	picture = models.ImageField(upload_to=content_file_trolley, blank=True)