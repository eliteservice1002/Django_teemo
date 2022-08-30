from django import forms

from .models import Purchase, Transport

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ('name', 'order_date', 'supplier', 'description', 'user')

class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = ('purchase', 'name', 'departure', 'arrival', 'description', 'container')