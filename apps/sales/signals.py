#Signal para atualizar estoque e faturamento
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.customers.models import Company
from apps.products.models import Product
from .models import Sale
from django.db import transaction
from django.db.models import F
    

@receiver(post_save, sender=Sale)
def update_stock_and_revenue(sender, instance, created, **kwargs):
    if created:
        # Atualiza o estoque
        with transaction.atomic():
            Product.objects.filter(pk=instance.product_id).update(stock=F('stock') - instance.quantity)
            Company.objects.filter(pk=instance.company_id).update(revenue=F('revenue') + instance.total_price)