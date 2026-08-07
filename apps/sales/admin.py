from django.contrib import admin
from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'quantity', 'total_price', 'sold_at')
    list_filter = ('sold_at',)
    search_fields = ('product__name', 'customer__name')
