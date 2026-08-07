# SmartHub-Django — CRM System

## Projeto de Seleção para o NADIC (IFRN)

---

# 🗺️ Planejamento Geral do Projeto

Este documento serve como guia de estudo e planejamento para construir um sistema **CRM** completo utilizando **Django** (Parte 4) e **Django REST Framework** (Parte 5).

---

# 📦 Parte 4 — Django (Backend Tradicional)

## 1. Ambiente Virtual e Setup Inicial

### Conceitos a aprender:
- **Ambiente virtual (`venv`)**: Isola as dependências do projeto do sistema.
- **`pip`**: Gerenciador de pacotes Python.
- **`requirements.txt`**: Arquivo que lista todas as dependências.

### Passos:
1. Criar ambiente virtual: `python -m venv venv`
2. Ativar o venv (Windows: `venv\Scripts\activate`)
3. Instalar Django: `pip install django`
4. Congelar dependências: `pip freeze > requirements.txt`

---
python -m venv venv
## 2. Projeto e Apps

### Conceitos a aprender:
- **Projeto Django**: É o "guarda-chuva" que contém configurações globais (`settings.py`, `urls.py`).
- **App Django**: Módulo que representa uma funcionalidade específica do sistema. Um projeto pode ter vários apps.

### Estrutura sugerida:

```
SmartHub-Django/
├── config/                 # Projeto (configurações)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── products/           # App de produtos
│   ├── sales/              # App de vendas
│   ├── customers/          # App de clientes
│   └── accounts/           # App de autenticação
├── templates/              # Templates HTML globais
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
├── media/                  # Uploads de usuários
├── manage.py
└── requirements.txt
```

### Comandos:
```bash
django-admin startproject config .
python manage.py startapp products apps/products
python manage.py startapp sales apps/sales
# ... etc
```

### Configuração no `settings.py`:
- Adicionar os apps em `INSTALLED_APPS`
- Configurar `STATIC_URL`, `MEDIA_URL`, `TEMPLATES`

---

## 3. URLs (Sistema de Roteamento)

### Conceitos a aprender:
- **`urlpatterns`**: Lista de rotas do Django.
- **`path()` e `re_path()`**: Funções para definir rotas.
- **`include()`**: Incluir URLs de outros apps (modularização).
- **Namespaces**: Agrupar rotas por app (ex: `products:list`).

### Estrutura:
```
config/urls.py → inclui → apps/products/urls.py
                        → apps/sales/urls.py
                        → apps/accounts/urls.py
```

---

## 4. Models (Banco de Dados)

### Conceitos a aprender:
- **Model**: Classe Python que representa uma tabela no banco.
- **Campos do Django**: `CharField`, `IntegerField`, `DecimalField`, `ForeignKey`, `DateTimeField`, etc.
- **`Meta` class**: Configurações como `ordering`, `verbose_name`.
- **`__str__`**: Representação legível do objeto.
- **Migrations**: Comandos `makemigrations` e `migrate`.

### Modelos sugeridos para o CRM:

### **products/models.py — Product**
```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
```

### **sales/models.py — Sale**
```python
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)
```

### **customers/models.py — Customer**
```python
class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### **Vínculo com Empresa (Owner)**
Para o requisito de "faturamento só pode ser acessado pelo dono", você precisará de um model `Company`:

```python
class Company(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

E o `Product` deve ter uma `ForeignKey` para `Company`.

---

## 5. Views (Lógica de Negócio)

### Conceitos a aprender:
- **Function-Based Views (FBV)**: Funções que recebem `request` e retornam `response`.
- **Class-Based Views (CBV)**: Classes que organizam a lógica em métodos como `get()`, `post()`.
- **`render()`**: Função para renderizar templates com contexto.
- **`redirect()`**: Redirecionar para outra URL.
- **`get_object_or_404()`**: Busca objeto ou retorna 404.

### Exemplos de View Functions (FBV):

```python
# products/views.py (FBV)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:list')
    else:
        form = ProductForm()
    return render(request, 'products/form.html', {'form': form})
```

### Exemplos de Class-Based Views (CBV):

```python
# products/views.py (CBV)
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('products:list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('products:list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('products:list')
```

### 📌 Regra de negócio importante: Venda → Atualizar Estoque + Faturamento

Sempre que uma venda for realizada:
1. **Diminuir `stock`** do produto vendido
2. **Aumentar `revenue`** da empresa associada

Isso pode ser feito:
- Sobrescrevendo o método `save()` ou `form_valid()` na view de criação de venda
- Ou usando **Django Signals** (`post_save`) para desacoplar a lógica

**Exemplo com signals:**

```python
# sales/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale

@receiver(post_save, sender=Sale)
def update_stock_and_revenue(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock -= instance.quantity
        product.save()

        company = product.company
        company.revenue += instance.total_price
        company.save()
```

---

## 6. Templates (Interface HTML)

### Conceitos a aprender:
- **Linguagem de template Django**: `{{ variavel }}`, `{% for %}`, `{% if %}`, `{% url %}`, `{% block %}`, `{% extends %}`.
- **Herança de templates**: `base.html` → `list.html`, `form.html`.
- **Filtros**: `{{ valor|default:"N/A" }}`, `{{ data|date:"d/m/Y" }}`.
- **Static files**: `{% load static %}`, `{% static 'css/style.css' %}`.

### Estrutura de templates:
```
templates/
├── base.html               # Template base (navbar, footer, estrutura HTML)
├── products/
│   ├── list.html
│   ├── form.html           # Create + Update (reutilizável)
│   └── confirm_delete.html
├── sales/
│   ├── list.html
│   └── form.html
├── customers/
│   ├── list.html
│   ├── form.html
│   └── detail.html
└── registration/
    ├── login.html
    └── register.html
```

---

## 7. Forms (Formulários)

### Conceitos a aprender:
- **`ModelForm`**: Gera formulário automaticamente a partir de um Model.
- **Validação**: Métodos `clean()` e `clean_<campo>()`.
- **CSRF Token**: `{% csrf_token %}` obrigatório em todo POST.
- **`widgets`**: Personalizar aparência dos campos.

### Exemplo:
```python
# products/forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }
```

---

## 8. FBV vs CBV — Quando usar cada uma?

| Característica | FBV | CBV |
|---|---|---|
| Simplicidade | ✅ Mais fácil para iniciantes | ❌ Curva de aprendizado maior |
| Reutilização | ❌ Código duplicado | ✅ Mixins e herança |
| Views padrão (CRUD) | ❌ Escrever tudo manualmente | ✅ `ListView`, `CreateView`, etc. |
| Lógica customizada | ✅ Fácil de customizar | ❌ Requer sobrescrever métodos |
| Código conciso | ❌ Mais verboso | ✅ Menos linhas |

**Recomendação**: Use **CBV** para operações CRUD padrão e **FBV** para lógicas mais específicas (como processar uma venda com validação de estoque).

---

## 9. PROJETO CRM — Funcionalidades (Parte 4)

### Funcionalidades obrigatórias:
1. ✅ **Cadastrar produto** (CRUD completo)
2. ✅ **Remover produto** (com confirmação)
3. ✅ **Editar produto**
4. ✅ **Gerenciar estoque** (definir quantidade inicial, atualizar ao vender)
5. ✅ **Realizar venda** → atualizar estoque automaticamente
6. ✅ **Faturamento** → atualizar automaticamente a cada venda

### Funcionalidades extras (diferencial):
- Dashboard com cards mostrando: total de produtos, estoque total, faturamento
- Filtro de produtos por nome/categoria
- Relatório de vendas por período
- Autenticação (login/logout)
- Empresa vinculada ao usuário logado

---

# 🌐 Parte 5 — Django REST Framework (API)

## 1. Requests e Responses no DRF

### Conceitos:
- **`Request` object**: Similar ao `HttpRequest` do Django, mas com `request.data` para JSON.
- **`Response` object**: Similar ao `HttpResponse`, mas retorna dados em JSON automaticamente.
- **Status codes**: `status.HTTP_201_CREATED`, `status.HTTP_400_BAD_REQUEST`, etc.
- **`@api_view` decorator**: Define que uma view function é uma API endpoint.

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET', 'POST'])
def product_list_api(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

---

## 2. API REST

### Conceitos:
- **REST**: Representational State Transfer.
- **Endpoints**: URLs que representam recursos.
- **Métodos HTTP**: GET (listar/detalhar), POST (criar), PUT/PATCH (atualizar), DELETE (remover).
- **Stateless**: Cada requisição contém toda informação necessária.

### Endpoints do CRM:
```
GET    /api/products/          → Listar produtos
POST   /api/products/          → Cadastrar produto
GET    /api/products/{id}/     → Detalhes do produto
PUT    /api/products/{id}/     → Editar produto
DELETE /api/products/{id}/     → Remover produto

GET    /api/sales/             → Listar vendas
POST   /api/sales/             → Realizar venda

GET    /api/company/revenue/   → Faturamento (só dono)

POST   /api/auth/register/     → Criar conta
POST   /api/auth/login/        → Login (obter token)
POST   /api/auth/logout/       → Logout
```

---

## 3. Model Serializers

### Conceitos:
- **Serializer**: Converte objetos Python (models) para JSON e vice-versa.
- **`ModelSerializer`**: Gera automaticamente campos baseados no model.
- **Validação**: `validate_<campo>()`, `validate()`.
- **Campos customizados**: `SerializerMethodField`.

```python
# products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'company_name', 'created_at']
        read_only_fields = ['id', 'created_at']
```

---

## 4. APIView e @api_view

### **APIView (Class-based)**:
```python
from rest_framework.views import APIView

class ProductListAPIView(APIView):
    def get(self, request):
        products = Product.objects.filter(company__owner=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

### **@api_view (Function-based)**:
```python
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list_api(request):
    ...
```

---

## 5. ViewSets e Routers

### Conceitos:
- **`ViewSet`**: Combina múltiplas views (list, create, retrieve, update, destroy) em uma classe.
- **`ModelViewSet`**: Já implementa CRUD completo automaticamente.
- **`Router`**: Gera URLs automaticamente para o ViewSet.

```python
# products/views.py (API)
from rest_framework.viewsets import ModelViewSet

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(company__owner=self.request.user)

    def perform_create(self, serializer):
        company = Company.objects.get(owner=self.request.user)
        serializer.save(company=company)
```

```python
# config/urls.py
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

Isso gera automaticamente:
- `GET /api/products/` → list
- `POST /api/products/` → create
- `GET /api/products/{id}/` → retrieve
- `PUT /api/products/{id}/` → update
- `PATCH /api/products/{id}/` → partial_update
- `DELETE /api/products/{id}/` → destroy

---

## 6. CRUD API (POST/GET/PUT/DELETE)

### Mapeamento:
| Ação | Método HTTP | Endpoint | ViewSet Method |
|---|---|---|---|
| Listar | GET | `/api/products/` | `.list()` |
| Criar | POST | `/api/products/` | `.create()` |
| Detalhar | GET | `/api/products/1/` | `.retrieve()` |
| Atualizar | PUT | `/api/products/1/` | `.update()` |
| Atualizar parcial | PATCH | `/api/products/1/` | `.partial_update()` |
| Remover | DELETE | `/api/products/1/` | `.destroy()` |

---

## 7. Autenticação (Sessão / JWT / OAuth2)

### Opções:

#### **Session Authentication** (mais simples, para web):
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ]
}
```

#### **JWT (JSON Web Token)** — Recomendado para APIs:
Usa-se a biblioteca `djangorestframework-simplejwt`:

```bash
pip install djangorestframework-simplejwt
```

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}
```

```python
# urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

### 📌 Plano de autenticação para o CRM:
1. Usuário faz **registro** → cria conta com `username`, `email`, `password`
2. Usuário faz **login** → recebe um **JWT token** (access + refresh)
3. Usuário envia o token no header **`Authorization: Bearer <token>`**
4. O Django Rest Framework valida o token e identifica o usuário

---

## 8. Permissões (DRF Permissions)

### Conceitos:
- **`IsAuthenticated`**: Apenas usuários logados.
- **`IsAdminUser`**: Apenas admins.
- **`IsAuthenticatedOrReadOnly`**: Logados podem tudo; não-logados só leitura.
- **`Custom Permission`**: Lógica específica (ex: só o dono da empresa).

### Permissão customizada para dono da empresa:
```python
# accounts/permissions.py
from rest_framework.permissions import BasePermission

class IsCompanyOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj é um Product, Sale, ou Company
        return obj.company.owner == request.user
```

### Aplicando no ViewSet:
```python
class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsCompanyOwner]

    def get_queryset(self):
        return Product.objects.filter(company__owner=self.request.user)
```

---

## 9. PROJETO — API do CRM (Requisitos)

### ✅ Endpoints obrigatórios:

1. **`POST /api/auth/register/`** → Criar conta
   - Campos: `username`, `email`, `password`, `company_name`
   - Cria o usuário + cria uma `Company` associada

2. **`POST /api/auth/login/`** → Login (retorna JWT)
   - Usa `TokenObtainPairView` do SimpleJWT

3. **`GET/POST /api/products/`** → Listar / Cadastrar produtos
   - Só para usuários autenticados
   - Produto vinculado à empresa do usuário

4. **`GET/PUT/DELETE /api/products/{id}/`** → Detalhar / Editar / Remover
   - Só o dono da empresa pode

5. **`GET /api/products/{id}/stock/`** → Detalhes do produto + estoque
   - Pode ser um campo extra no serializer ou um endpoint dedicado

6. **`GET /api/company/revenue/`** → Faturamento da empresa
   - **Só o dono da empresa pode acessar**
   - Retorna: `{ "company": "Nome", "revenue": 15000.00 }`

---

# 🧱 Estrutura Final Recomendada do Projeto

```
SmartHub-Django/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── products/
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── sales/
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   └── views.py
│   └── customers/
│       ├── migrations/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── urls.py
│       └── views.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── registration/
│   │   ├── login.html
│   │   └── register.html
│   ├── products/
│   │   ├── list.html
│   │   ├── form.html
│   │   └── confirm_delete.html
│   ├── sales/
│   │   ├── list.html
│   │   └── form.html
│   └── customers/
│       ├── list.html
│       └── form.html
├── static/
│   └── css/
│       └── style.css
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

---

# 📚 Ordem de Estudo Sugerida

## Semana 1: Fundamentos Django
1. [ ] Criar ambiente virtual e instalar Django
2. [ ] Criar projeto e entender `settings.py`
3. [ ] Criar primeiro app (products) com Model
4. [ ] Fazer migrações e aprender sobre banco de dados
5. [ ] Criar uma View Function simples e uma URL

## Semana 2: CRUD Completo
1. [ ] Implementar Model Product completo
2. [ ] Criar Forms com ModelForm
3. [ ] Criar Templates (list, form, confirm_delete)
4. [ ] Implementar ListView, CreateView, UpdateView, DeleteView
5. [ ] Testar CRUD completo no navegador

## Semana 3: Vendas e Lógica de Negócio
1. [ ] Criar Model Sale e Company
2. [ ] Implementar lógica de venda (FBV)
3. [ ] Configurar Django Signals para atualizar estoque + faturamento
4. [ ] Criar template de dashboard com métricas
5. [ ] Adicionar autenticação (login/logout)

## Semana 4: Django REST Framework
1. [ ] Instalar `djangorestframework` e `djangorestframework-simplejwt`
2. [ ] Criar Serializers para Product, Sale, Company
3. [ ] Implementar ProductViewSet com ModelViewSet
4. [ ] Configurar Router e URLs da API
5. [ ] Testar endpoints com Postman ou Insomnia

## Semana 5: Autenticação e Permissões na API
1. [ ] Criar endpoint de registro (`/api/auth/register/`)
2. [ ] Configurar JWT (login com token)
3. [ ] Adicionar permissões customizadas (IsCompanyOwner)
4. [ ] Criar endpoint de faturamento (só dono)
5. [ ] Testar fluxo completo: registro → login → CRUD protegido

---

# 🎯 Checklist Final do Projeto

## Parte 4 — Django (CRM)
- [ ] Ambiente virtual configurado
- [ ] Projeto com estrutura modular (apps separados)
- [ ] Model Product com campos (nome, descrição, preço, estoque)
- [ ] Model Sale vinculado ao Product
- [ ] Model Company vinculado ao User (owner)
- [ ] CRUD de Products (FBV ou CBV)
- [ ] Venda atualiza estoque automaticamente
- [ ] Venda atualiza faturamento da empresa
- [ ] Templates responsivos e organizados
- [ ] Autenticação (login/logout)

## Parte 5 — Django REST Framework (API)
- [ ] Serializers criados para todos os models
- [ ] ProductViewSet com CRUD completo
- [ ] Router configurado (DefaultRouter)
- [ ] Endpoint de registro de usuário
- [ ] Endpoint de login (JWT)
- [ ] Permissão IsAuthenticated em todos os endpoints
- [ ] Permissão customizada para dono da empresa
- [ ] Endpoint de detalhes do produto + estoque
- [ ] Endpoint de faturamento (só dono)
- [ ] Testes manuais com Postman/Insomnia

---

# 💡 Dicas para se Destacar

1. **Use Bootstrap ou Tailwind** nos templates — uma interface bonita impressiona
2. **Adicione um dashboard** com gráficos (Chart.js) mostrando vendas, estoque, faturamento
3. **Escreva testes** (`tests.py`) — mostra profissionalismo
4. **Documente a API** com Swagger/DRF-YASG
5. **Use variáveis de ambiente** para dados sensíveis (`python-decouple`)
6. **Faça commits organizados** no Git — mostra versionamento profissional
7. **Adicione um `docker-compose.yml`** com PostgreSQL — diferencial enorme

---

> **Boa sorte no processo seletivo do NADIC!** 🚀
