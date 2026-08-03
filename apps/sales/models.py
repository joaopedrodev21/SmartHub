from django.db import models
from apps.products.models import Product
from apps.customers.models import Company

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales', null=True, blank=True )
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.product.name}"