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

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Customer.objects.filter(company=company)
        return Customer.objects.none()

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/form.html'
    success_url = reverse_lazy('customers:customer_list')

    def form_valid(self, form):
        company = self.request.user.companies.first()
        if company:
            form.instance.company = company
        return super().form_valid(form)

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/form.html'
    success_url = reverse_lazy('customers:customer_list')

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Customer.objects.filter(company=company)
        return Customer.objects.none()

    def form_valid(self, form):
        company = self.request.user.companies.first()
        if company:
            form.instance.company = company
        return super().form_valid(form)

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Customer.objects.filter(company=company)
        return Customer.objects.none()