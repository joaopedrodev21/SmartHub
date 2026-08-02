from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.products.views_api import (
    register,
    login,
    ProductViewSet,
    CompanyRevenueAPIView,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # Auth
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),

    # Company Revenue
    path('company/revenue/', CompanyRevenueAPIView.as_view(), name='company-revenue'),
]

urlpatterns += router.urls