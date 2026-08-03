from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from apps.customers.models import Company
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Product
from .serializers import ProductSerializer, CustomerSerializer, CompanySerializer


# Auth para Regitro de usuários 
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    company_name = request.data.get('company_name') or f"{username}'s Company"

    if not username or not email or not password:
        return Response({'error': 'Preencha todos os campos'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Usuário já existe'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    company = Company.objects.create(
        name=company_name,
        email=user.email,
        owner=user
    )
    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })

#Auth para Login de usuários
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })


# Products
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(company__owner=self.request.user)

    def perform_create(self, serializer):
        company = self.request.user.companies.first()
        if not company:
            company = Company.objects.create(
                name=f"{self.request.user.username}'s Company",
                email=self.request.user.email,
                owner=self.request.user,
            )
        serializer.save(company=company)

    @action(detail=True, methods=['get'], url_path='stock')
    def stock(self, request, pk=None):
        product = self.get_object()
        return Response({
            'id': product.id,
            'name': product.name,
            'stock': product.stock,
        })

# Company Revenue (só dono)
class CompanyRevenueAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            company = request.user.companies.first()
            if not company:
                return Response({'error': 'Nenhuma empresa encontrada'}, status=status.HTTP_404_NOT_FOUND)

            if company.owner != request.user:
                return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)

            return Response({
                'company': company.name,
                'revenue': company.revenue,
            })
        except Exception:
            return Response({'error': 'Erro ao buscar faturamento'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)