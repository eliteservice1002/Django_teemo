from django import forms
from .models import User, Stock, Contact, Client, Command, Mailing, UserRole


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'picture', 'email', 'telephone')
        widgets = {
            'picture': forms.FileInput(attrs={'class':'custom-file-input','onchange':'readURL(this);'}),
            'first_name': forms.TextInput(attrs={'class':'form-control', }),
            'last_name': forms.TextInput(attrs={'class':'form-control', }),
            'email': forms.TextInput(attrs={'class':'form-control', 'required': True, 'type':'email'}),
            'telephone': forms.TextInput(attrs={'class':'form-control', }),
            'username': forms.TextInput(attrs={'class':'form-control', }),
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ('name', 'reference', 'quantity', 'picture', 'category', 'user', 'minium', 'b_group', 'pdf', 'location', 'width', 'height', 'depth', 'weight', 'sale_price', 'tax')



class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'picture', 'address', 'country', 'notes', 'telephone', 'mobile', 'email', 'web', 'products', 'pdf', 'user', 'nif')

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'picture', 'country', 'notes', 'telephone', 'mobile', 'email', 'web', 'products', 'pdf', 'parent', 'user', 'b_client', 'nif', 'address', 'state', 'postalcode', 'mail_list')

class CommandForm(forms.ModelForm):
    class Meta:
        model = Command
        fields = ('name', 'date', 'group', 'quantity', 'worker', 'user')

class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ('name', 'content', 'mail_list')

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = ('supplier_add', 'supplier_up', 'supplier_del','lead_add', 'lead_up', 'lead_del','mail_add', 'mail_up', 'mail_del','product_add', 'product_up', 'product_del','purchase_add', 'purchase_up', 'purchase_del','transport_add', 'transport_up', 'transport_del','manufact_add', 'manufact_up', 'manufact_del','outcome_add', 'outcome_up', 'outcome_del','trolley_add', 'trolley_up', 'trolley_del','invent_add', 'invent_up', 'invent_del','offer_add', 'offer_up', 'offer_del','time_add', 'time_up', 'time_del', 'setting_add', 'setting_up', 'setting_del')