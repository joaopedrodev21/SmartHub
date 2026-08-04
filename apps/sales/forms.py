from django import forms
from apps.products.models import Product
from apps.customers.models import Customer
from .models import Sale


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'customer', 'quantity']
        labels = {
            'product': 'Produto',
            'customer': 'Cliente',
            'quantity': 'Quantidade',
        }
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
        customer = cleaned_data.get('customer')
        quantity = cleaned_data.get('quantity')

        if product and quantity and quantity > product.stock:
            self.add_error('quantity', 'Quantidade superior ao estoque disponível.')

        # Necessário um cliente para registrar a venda
        if customer is None:
            self.add_error('customer', 'Selecione um cliente para a venda.')

        # Necessário que o produto e o cliente pertençam à mesma empresa que o usuário atual
        if self.user is not None and product is not None and customer is not None:
            company = self.user.companies.first()
            if company:
                if product.company_id != company.id:
                    self.add_error('product', 'Produto inválido para a sua empresa.')
                if customer.company_id != company.id:
                    self.add_error('customer', 'Cliente inválido para a sua empresa.')

        return cleaned_data
