from django.db import models
from apps.products.models import Product
from apps.customers.models import Company, Customer
from django.core.exceptions import ValidationError

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales', null=True, blank=True )
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.product.name}"
    
    def clean(self):
        super().clean()
        if self.product_id and self.quantity is not None:
            if self.quantity > self.product.stock:
                raise ValidationError(
                    {'quantity':'Quantidade superior ao estoque disponível.' }
                )
    def save(self, *args, **kwargs):
        self.full_clean() # Valida os campos antes de salvar
        super().save(*args, **kwargs) # Chama o método save() da classe pai para salvar o objeto no banco de dados