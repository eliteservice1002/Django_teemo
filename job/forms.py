from django import forms

from .models import Job, JobCandidate

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('name', 'picture', 'category', 'description', 'skills', 'user')

class CandidateForm(forms.ModelForm):
    class Meta:
        model = JobCandidate
        fields = ('name', 'picture', 'pdf', 'description', 'tag', 'job')