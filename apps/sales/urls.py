from django.urls import path 
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SaleListView, name='sale_list'),
    path('create/', views.SaleCreateView, name='sale_create'),
]
