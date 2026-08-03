from django.shortcuts import render, redirect
from .models import Sale
from .forms import SaleForm
from django.contrib.auth.decorators import login_required


@login_required
def sale_list_view(request):
    sales = Sale.objects.select_related('product').filter(company__owner=request.user)
    return render(request, 'sales/list.html', {'sales': sales})


@login_required
def sale_create_view(request):
    if request.method == 'POST':
        form = SaleForm(request.POST, user=request.user)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.total_price = sale.product.price * sale.quantity
            sale.company = request.user.companies.first()
            sale.save()
        return redirect('sales:sale_list')
    else:
        form = SaleForm(user=request.user)

    return render(request, 'sales/form.html', {'form': form})