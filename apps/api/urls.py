from django.urls import path
from apps.products.views_api import register, login, ProductListCreateAPIView, ProductDetailAPIView, ProductStockDetailAPIView, CompanyRevenueAPIView

urlpatterns = [
    # Auth
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    
    # Products
    path('products/', ProductListCreateAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('products/<int:pk>/stock/', ProductStockDetailAPIView.as_view(), name='product-stock'),
    
    # Company Revenue
    path('company/revenue/', CompanyRevenueAPIView.as_view(), name='company-revenue'),
]