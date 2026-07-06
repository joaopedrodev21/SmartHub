from rest_framework import serializers
from .models import Product
from apps.sales.models import Sale
from apps.customers.models import Company, Customer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'brand', 'company', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'address']
        read_only_fields = ['id']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'email', 'phone', 'address', 'revenue', 'owner']
        read_only_fields = ['id', 'revenue', 'owner']