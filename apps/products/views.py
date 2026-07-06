from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product
from .forms import ProductForm
from apps.sales.models import Sale
from apps.customers.models import Company
from django.db.models import Sum, Count

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    total_products = Product.objects.count()
    total_stock = Product.objects.aggregate(Sum('stock'))['stock__sum'] or 0
    total_revenue = Company.objects.aggregate(Sum('revenue'))['revenue__sum'] or 0
    total_sales = Sale.objects.count()
    recent_sales = Sale.objects.select_related('product').order_by('-sold_at')[:5]

    context = {
        'total_products': total_products,
        'total_stock': total_stock,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'recent_sales': recent_sales,
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('products:product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('products:product_list')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('products:product_list')