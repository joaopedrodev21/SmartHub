from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from apps.customers.models import Customer, Company
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
        if not company:
            company = Company.objects.create(
                name=f"{self.request.user.first_name or self.request.user.username} Company",
                email=self.request.user.email,
                owner=self.request.user,
            )
        form.instance.company = company
        response = super().form_valid(form)
        messages.success(self.request, 'Cliente criado com sucesso!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Não foi possível criar o cliente. Verifique os campos.')
        return super().form_invalid(form)

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
        if not company:
            company = Company.objects.create(
                name=f"{self.request.user.first_name or self.request.user.username} Company",
                email=self.request.user.email,
                owner=self.request.user,
            )
        form.instance.company = company
        response = super().form_valid(form)
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Não foi possível atualizar o cliente. Verifique os campos.')
        return super().form_invalid(form)

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Customer.objects.filter(company=company)
        return Customer.objects.none()

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Cliente excluído com sucesso!')
        return response


class CustomerDetailView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/detail.html'
    success_url = reverse_lazy('customers:customer_list')

    def get_queryset(self):
        company = self.request.user.companies.first()
        if company:
            return Customer.objects.filter(company=company)
        return Customer.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Não foi possível atualizar o cliente. Verifique os campos.')
        return super().form_invalid(form)
