from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from django.contrib.auth.models import User
from apps.customers.models import Company
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.customers.permissions import IsCompanyOwner
from .models import Product
from .serializers import ProductSerializer, CustomerSerializer, CompanySerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email

# Auth para Registro de usuários
@extend_schema(
    tags=['Autenticação'],
    summary='Registro de novo usuário/empresa',
    description='Cria um usuário e uma empresa associada, retornando os tokens JWT.',
    request=inline_serializer(
        name='RegisterRequest',
        fields={
            'username': drf_serializers.CharField(),
            'email': drf_serializers.EmailField(),
            'password': drf_serializers.CharField(write_only=True),
            'company_name': drf_serializers.CharField(required=False),
        },
    ),
    responses={
        201: inline_serializer(
            name='RegisterResponse',
            fields={
                'refresh': drf_serializers.CharField(),
                'access': drf_serializers.CharField(),
                'user': inline_serializer(
                    name='UserInfo',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'username': drf_serializers.CharField(),
                        'email': drf_serializers.EmailField(),
                    },
                ),
            },
        ),
        400: inline_serializer(
            name='ErrorResponse',
            fields={'error': drf_serializers.ListField(child=drf_serializers.CharField())},
        ),
    },
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    company_name = request.data.get('company_name') or f"{username}'s Company"

    if not username or not email or not password:
        return Response({'error': 'Preencha todos os campos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_email(email)
    except DjangoValidationError as e:
        return Response({'error': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except DjangoValidationError as e:
        return Response({'error': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

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

# Auth para Login de usuários
@extend_schema(
    tags=['Autenticação'],
    summary='Login de usuário',
    description='Autentica um usuário e retorna os tokens JWT (access e refresh).',
    request=inline_serializer(
        name='LoginRequest',
        fields={
            'username': drf_serializers.CharField(),
            'password': drf_serializers.CharField(write_only=True),
        },
    ),
    responses={
        200: inline_serializer(
            name='LoginResponse',
            fields={
                'refresh': drf_serializers.CharField(),
                'access': drf_serializers.CharField(),
                'user': inline_serializer(
                    name='UserInfoLogin',
                    fields={
                        'id': drf_serializers.IntegerField(),
                        'username': drf_serializers.CharField(),
                        'email': drf_serializers.EmailField(),
                    },
                ),
            },
        ),
        401: inline_serializer(
            name='ErrorResponse401',
            fields={'error': drf_serializers.CharField()},
        ),
    },
)
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


# Classe para gerenciar produtos
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'brand', 'category']
    ordering_fields = ['name', 'price', 'stock', 'created_at']
    ordering = ['-created_at']
    lookup_value_regex = r'\d+'

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
    @extend_schema(
        tags=['Produtos'],
        summary='Consultar estoque do produto',
        description='Retorna o estoque atual de um produto específico.',
        responses={
            200: inline_serializer(
                name='StockResponse',
                fields={
                    'id': drf_serializers.IntegerField(),
                    'name': drf_serializers.CharField(),
                    'stock': drf_serializers.IntegerField(),
                },
            ),
        },
    )
    def stock(self, request, pk=None):
        product = self.get_object()
        return Response({
            'id': product.id,
            'name': product.name,
            'stock': product.stock,
        })

# Company Revenue (só dono)
class CompanyRevenueAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyOwner]

    @extend_schema(
        tags=['Empresa'],
        summary='Faturamento da empresa',
        description='Retorna o nome e o faturamento total da empresa do usuário autenticado.',
        responses={
            200: inline_serializer(
                name='CompanyRevenueResponse',
                fields={
                    'company': drf_serializers.CharField(),
                    'revenue': drf_serializers.DecimalField(max_digits=15, decimal_places=2),
                },
            ),
            404: inline_serializer(
                name='ErrorResponse404',
                fields={'error': drf_serializers.CharField()},
            ),
        },
    )
    def get(self, request):
        company = request.user.companies.first()
        if not company:
            return Response({'error': 'Nenhuma empresa encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'company': company.name,
            'revenue': company.revenue,
        })
