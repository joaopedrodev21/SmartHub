from django.shortcuts import render, redirect
from .models import Sale
from .forms import SaleForm
from django.contrib.auth.decorators import login_required


@login_required
def sale_list_view(request):
    sales = Sale.objects.select_related('product').all()
    return render(request, 'sales/list.html', {'sales': sales})


@login_required
def sale_create_view(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        #Salvamento do objeto Sale com o total_price calculado
        if form.is_valid():
            sale = form.save(commit=False)
            sale.total_price = sale.product.price * sale.quantity
            sale.save()
            return redirect('sales:sale_list')
    else:
        form = SaleForm()

    return render(request, 'sales/form.html', {'form': form})