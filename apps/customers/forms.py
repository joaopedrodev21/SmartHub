from django import forms
from .models import Customer 

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer 
        fields = ['name', 'email', 'phone_number', 'address']
        labels = {
            'name': 'Nome',
            'email': 'E-mail',
            'phone_number': 'Telefone',
            'address': 'Endereço',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@email.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Rua, número, bairro, cidade'}),
        }
