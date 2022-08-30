from django.db import models
import os
# Create your models here.
from backend.models import User

def content_file_job(instance, filename):
    return 'job/{1}'.format(instance, filename)

def content_file_candidate(instance, filename):
    return 'candidate/{1}'.format(instance, filename)

def content_file_candidate_pdf(instance, filename):
    return 'candidate/pdf/{1}'.format(instance, filename)

class Job(models.Model):
    name = models.CharField(unique=True, max_length=150)
    picture = models.ImageField(upload_to=content_file_job, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']

class JobFavorite(models.Model):
    name = models.CharField(max_length=150)
    category = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.name
class JobCandidate(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(unique=True, max_length=150)
    picture = models.ImageField(upload_to=content_file_candidate, blank=True)
    description = models.TextField(blank=True)
    pdf = models.FileField(upload_to=content_file_candidate_pdf, blank=True)
    tag = models.CharField(max_length=250, blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    def filename(self):
        return os.path.basename(self.pdf.name)
    class Meta:
        ordering = ['-id']