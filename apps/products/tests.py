import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from apps.customers.models import Company
from apps.products.models import Product


class ProductTenantIsolationTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='tenant_a', email='a@example.com', password='12345678')
        self.user_b = User.objects.create_user(username='tenant_b', email='b@example.com', password='12345678')

        self.company_a = Company.objects.create(name='Company A', email='a@company.com', owner=self.user_a)
        self.company_b = Company.objects.create(name='Company B', email='b@company.com', owner=self.user_b)

        self.product_a = Product.objects.create(
            name='Product A', description='A', price='10.00', stock=5,
            category='hardware', brand='Brand A', company=self.company_a,
        )
        self.product_b = Product.objects.create(
            name='Product B', description='B', price='20.00', stock=3,
            category='hardware', brand='Brand B', company=self.company_b,
        )

    def test_user_sees_only_products_from_own_company(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('products:product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product_a.name)
        self.assertNotContains(response, self.product_b.name)


class ProductAPITests(TestCase):
    """Testes da API REST (registro/login JWT, CRUD de produtos e faturamento)."""

    def setUp(self):
        self.username = 'api_user'
        self.email = 'api@example.com'
        self.password = 'SenhaForte@123'
        self.user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.company = Company.objects.create(
            name='API Company', email='company@example.com', owner=self.user
        )

    def _auth_header(self, username=None, password=None):
        """Faz login via endpoint e retorna o header de autenticação JWT."""
        username = username or self.username
        password = password or self.password
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        return {'HTTP_AUTHORIZATION': f"Bearer {response.json()['access']}"}

    # ---------- Registro ----------
    def test_register_cria_usuario_empresa_e_retorna_jwt(self):
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps({
                'username': 'novo_user',
                'email': 'novo@example.com',
                'password': 'OutraSenha@123',
                'company_name': 'Nova Empresa',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['user']['username'], 'novo_user')

        company = Company.objects.get(owner__username='novo_user')
        self.assertEqual(company.name, 'Nova Empresa')
        self.assertEqual(company.owner.username, 'novo_user')

    def test_register_rejeita_senha_fraca(self):
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps({'username': 'fraco', 'email': 'fraco@example.com', 'password': '123'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejeita_email_invalido(self):
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps({'username': 'email_ruim', 'email': 'invalido', 'password': 'SenhaForte@123'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejeita_username_duplicado(self):
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps({'username': self.username, 'email': 'outro@example.com', 'password': 'SenhaForte@123'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- Login ----------
    def test_login_retorna_jwt_com_credenciais_validas(self):
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': self.username, 'password': self.password}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_login_credenciais_invalidas(self):
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': self.username, 'password': 'errada'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- Refresh Token ----------
    def test_refresh_renova_access_token(self):
        login = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': self.username, 'password': self.password}),
            content_type='application/json',
        ).json()

        response = self.client.post(
            '/api/auth/refresh/',
            data=json.dumps({'refresh': login['refresh']}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())

    def test_refresh_rejeita_token_invalido(self):
        response = self.client.post(
            '/api/auth/refresh/',
            data=json.dumps({'refresh': 'token-invalido'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- Proteção ----------
    def test_produtos_exigem_autenticacao(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
# ---------- CRUD ----------
    def test_crud_produtos_autenticado(self):
        headers = self._auth_header()
        payload = {
            'name': 'Teclado Mecânico',
            'description': 'Switch red',
            'price': '199.90',
            'stock': 10,
            'category': 'peripheral',
            'brand': 'Redragon',
            'company': self.company.id,
        }

        # Create
        response = self.client.post(
            '/api/products/', data=json.dumps(payload),
            content_type='application/json', **headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product_id = response.json()['id']
        self.assertEqual(response.json()['company'], self.company.id)

        # List
        response = self.client.get('/api/products/', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # A resposta agora é paginada: dict com 'count', 'next' e 'results'
        self.assertIn('results', response.data)
        names = [item['name'] for item in response.data['results']]
        self.assertIn('Teclado Mecânico', names)

        # Retrieve (detalhe com estoque)
        response = self.client.get(f'/api/products/{product_id}/', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['stock'], 10)

        # Update (PUT)
        payload['price'] = '149.90'
        payload['stock'] = 7
        response = self.client.put(
            f'/api/products/{product_id}/', data=json.dumps(payload),
            content_type='application/json', **headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['price'], '149.90')
        self.assertEqual(response.json()['stock'], 7)

        # Delete
        response = self.client.delete(f'/api/products/{product_id}/', **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_produto_detalhe_estoque_action(self):
        headers = self._auth_header()
        product = Product.objects.create(
            name='Placa de Vídeo', price='2500.00', stock=3,
            category='hardware', company=self.company,
        )
        response = self.client.get(f'/api/products/{product.id}/stock/', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], product.id)
        self.assertEqual(response.json()['name'], 'Placa de Vídeo')
        self.assertEqual(response.json()['stock'], 3)

    def test_tenant_isolation_na_api(self):
        product = Product.objects.create(
            name='Produto da Empresa A', price='10.00', stock=5,
            category='hardware', company=self.company,
        )
        user_b = User.objects.create_user(
            username='api_user_b', email='b@example.com', password='Senha@123'
        )
        Company.objects.create(name='Company B', email='b@co.com', owner=user_b)
        headers_b = self._auth_header('api_user_b', 'Senha@123')

        list_response = self.client.get('/api/products/', **headers_b)
        names = [item['name'] for item in list_response.data['results']]
        self.assertNotIn(product.name, names)

        detail_response = self.client.get(f'/api/products/{product.id}/', **headers_b)
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------- Busca, Ordenação e Paginação ----------
    def test_busca_por_nome_e_marca(self):
        headers = self._auth_header()
        Product.objects.create(
            name='Mouse Gamer', price='99.90', stock=5,
            category='peripheral', brand='Redragon', company=self.company,
        )
        Product.objects.create(
            name='Teclado Gamer', price='199.90', stock=3,
            category='peripheral', brand='Logitech', company=self.company,
        )
        Product.objects.create(
            name='Headset', price='149.90', stock=4,
            category='accessory', brand='HyperX', company=self.company,
        )

        # Busca por nome
        response = self.client.get('/api/products/?search=gamer', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['results']]
        self.assertIn('Mouse Gamer', names)
        self.assertIn('Teclado Gamer', names)
        self.assertNotIn('Headset', names)

        # Busca por marca
        response = self.client.get('/api/products/?search=redragon', **headers)
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, ['Mouse Gamer'])

    def test_ordenacao_por_preco(self):
        headers = self._auth_header()
        Product.objects.create(
            name='A', price='30.00', stock=5, company=self.company,
        )
        Product.objects.create(
            name='B', price='10.00', stock=5, company=self.company,
        )
        Product.objects.create(
            name='C', price='20.00', stock=5, company=self.company,
        )

        response = self.client.get('/api/products/?ordering=price', **headers)
        prices = [item['price'] for item in response.data['results']]
        self.assertEqual(prices, ['10.00', '20.00', '30.00'])

        response = self.client.get('/api/products/?ordering=-price', **headers)
        prices = [item['price'] for item in response.data['results']]
        self.assertEqual(prices, ['30.00', '20.00', '10.00'])

    def test_paginacao(self):
        headers = self._auth_header()
        # Cria mais produtos que o PAGE_SIZE (10)
        for i in range(15):
            Product.objects.create(
                name=f'Produto {i}', price='10.00', stock=5,
                company=self.company,
            )

        response = self.client.get('/api/products/', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 15)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])

        response_page2 = self.client.get('/api/products/?page=2', **headers)
        self.assertEqual(len(response_page2.data['results']), 5)
        self.assertIsNone(response_page2.data['next'])

    # ---------- Faturamento ----------
    def test_revenue_somente_dono(self):
        headers = self._auth_header()
        response = self.client.get('/api/company/revenue/', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['company'], 'API Company')
        self.assertEqual(Decimal(str(response.json()['revenue'])), Decimal('0.00'))

    def test_revenue_negado_para_usuario_sem_empresa(self):
        User.objects.create_user(
            username='sem_empresa', email='sem@example.com', password='Senha@123'
        )
        headers = self._auth_header('sem_empresa', 'Senha@123')
        response = self.client.get('/api/company/revenue/', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)