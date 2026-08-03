from django import forms
from apps.products.models import Product
from apps.customers.models import Customer
from .models import Sale


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'customer', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user is not None:
            company = self.user.companies.first()
            if company:
                self.fields['product'].queryset = Product.objects.filter(company=company)
                self.fields['customer'].queryset = Customer.objects.filter(company=company)
            else:
                self.fields['product'].queryset = Product.objects.none()
                self.fields['customer'].queryset = Customer.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if product and quantity and quantity > product.stock:
            self.add_error('quantity', 'Quantidade superior ao estoque disponível.')

        return cleaned_data
