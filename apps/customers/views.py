from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from apps.customers.models import Customer
from .forms import CustomerForm

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer 
    template_name = 'customers/list.html'
    context_object_name = 'customers'

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer 
    form_class = CustomerForm
    template_name = 'customers/form.html'
    success_url = reverse_lazy('customers:customer_list')

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/form.html'
    success_url = reverse_lazy('customers:customer_list')

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer 
    template_name = 'customers/confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')