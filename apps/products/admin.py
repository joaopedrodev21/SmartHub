from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'stock', 'company']
    list_filter = ['category', 'brand']
    search_fields = ['name', 'brand']
