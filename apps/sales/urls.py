from django.urls import path 
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list_view, name='sale_list'),
    path('create/', views.sale_create_view, name='sale_create'),
]