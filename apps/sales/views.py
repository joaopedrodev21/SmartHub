from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Sale
from .forms import SaleForm
from django.contrib.auth.decorators import login_required


@login_required
def sale_list_view(request):
    sales = Sale.objects.select_related('product', 'customer').filter(company__owner=request.user)
    return render(request, 'sales/list.html', {'sales': sales})


@login_required
def sale_create_view(request):
    company = request.user.companies.first()

    # Se não houver empresa ou se a empresa não tiver clientes, redirecionar para a criação de clientes
    if company is None or not company.customers.exists():
        messages.error(request, 'É necessário cadastrar ao menos um cliente antes de registrar vendas.')
        return redirect('customers:customer_create')

    if request.method == 'POST':
        form = SaleForm(request.POST, user=request.user)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.total_price = sale.product.price * sale.quantity
            sale.company = company
            sale.save()
            messages.success(request, 'Venda registrada com sucesso!')
            return redirect('sales:sale_list')
        messages.error(request, 'Não foi possível registrar a venda. Verifique os dados.')
    else:
        form = SaleForm(user=request.user)

    return render(request, 'sales/form.html', {'form': form})
