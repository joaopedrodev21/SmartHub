#Signal para atualizar estoque e faturamento
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale

@receiver(post_save, sender=Sale)
def update_stock_and_revenue(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        # Atualiza o estoque
        product.stock -= instance.quantity
        product.save()

        # Atualiza o faturamento da empresa
        company = product.company
        company.revenue += instance.total_price
        company.save()
