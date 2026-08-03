from urllib import request

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib import messages

from .models import Product
from .forms import ProductForm, EmailLoginForm, RegisterForm
from apps.sales.models import Sale
from apps.customers.models import Company

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    total_products = Product.objects.filter(company__owner=request.user).count()
    total_stock = Product.objects.filter(company__owner=request.user).aggregate(Sum('stock'))['stock__sum'] or 0
    total_revenue = Company.objects.filter(owner=request.user).aggregate(Sum('revenue'))['revenue__sum'] or 0
    total_sales = Sale.objects.filter(company__owner=request.user).count()
    recent_sales = Sale.objects.select_related('product').filter(company__owner=request.user).order_by('-sold_at')[:5]

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


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = EmailLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.user_cache
        login(request, user)
        messages.success(request, 'Login realizado com sucesso!')
        return redirect('dashboard')

    return render(request, 'registration/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        base_username = email.split('@')[0].replace('.', '').replace('_', '')
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{suffix}'
            suffix += 1

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = name
        user.save()

        company_name = form.cleaned_data.get('company_name') or f'{name} Company'
        Company.objects.create(
            name=company_name,
            email=user.email,
            owner=user,
        )

        messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
        return redirect('login')

    return render(request, 'registration/register.html', {'form': form})


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Product.objects.filter(company=company)
        return Product.objects.none()

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('products:product_list')

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Product.objects.filter(company=company)
        return Product.objects.none()

    def form_valid(self, form):
        company = self.request.user.companies.first()
        if not company:
            company = Company.objects.create(
                name=f"{self.request.user.first_name or self.request.user.username} Company",
                email=self.request.user.email,
                owner=self.request.user,
            )
        form.instance.company = company
        response = super().form_valid(form)
        messages.success(self.request, 'Produto criado com sucesso!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Não foi possível criar o produto. Verifique os campos.')
        return super().form_invalid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('products:product_list')

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Product.objects.filter(company=company)
        return Product.objects.none()

    def form_valid(self, form):
        company = self.request.user.companies.first()
        if not company:
            company = Company.objects.create(
                name=f"{self.request.user.first_name or self.request.user.username} Company",
                email=self.request.user.email,
                owner=self.request.user,
            )
        form.instance.company = company
        response = super().form_valid(form)
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Não foi possível atualizar o produto. Verifique os campos.')
        return super().form_invalid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('products:product_list')

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Product.objects.filter(company=company)
        return Product.objects.none()

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Produto excluído com sucesso!')
        return response