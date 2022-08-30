from django.db import models
import os
# Create your models here.
from backend.models import User, Stock, Task

class TimeSheet(models.Model):
    date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    class Meta:
        ordering = ['-date']

class TimeSheetItem(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    finished = models.BooleanField(blank=True, null=True, default=False)
    timesheet = models.ForeignKey(TimeSheet, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['start_time', 'end_time']

class TimeSheetFavorite(models.Model):
    name = models.CharField(max_length=150)
    owner = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name