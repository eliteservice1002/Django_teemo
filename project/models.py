from django.db import models
from backend.models import User, Client



# Create your models here.
class ProjectColumn(models.Model):
    name = models.CharField(unique=True, max_length=150)
    position = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']

# Create your models here.
class ProjectItem(models.Model):
    name = models.CharField(unique=True, max_length=150)
    user = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']