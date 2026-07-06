from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('pc', 'PC Completo'),
        ('console', 'Console'),
        ('peripheral', 'Periférico'),
        ('hardware', 'Hardware/Componente'),
        ('game', 'Jogo'),
        ('accessory', 'Acessório'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='hardware')
    brand = models.CharField(max_length=100, blank=True)
    company = models.ForeignKey('customers.Company', on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
