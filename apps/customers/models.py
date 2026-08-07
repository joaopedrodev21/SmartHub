from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company = models.ForeignKey('customers.Company', on_delete=models.CASCADE, related_name='customers', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Company (models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='companies')
    revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name