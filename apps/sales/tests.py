from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.customers.models import Company, Customer
from apps.products.models import Product
from apps.sales.models import Sale


class SaleStockValidationTests(TestCase):
    """Testes da validação de estoque e da atualização automática de estoque/faturamento."""

    def setUp(self):
        self.user = User.objects.create_user(username='sale_owner', password='Senha@123')
        self.company = Company.objects.create(
            name='Loja Teste', email='loja@example.com', owner=self.user
        )
        self.product = Product.objects.create(
            name='Mouse Gamer', price='99.90', stock=5,
            category='peripheral', company=self.company,
        )
        self.customer = Customer.objects.create(
            name='Cliente Teste', email='cliente@example.com', company=self.company
        )

    def test_venda_acima_do_estoque_e_bloqueada(self):
        with self.assertRaises(ValidationError) as ctx:
            Sale.objects.create(
                product=self.product, quantity=6, total_price='599.40',
                company=self.company, customer=self.customer,
            )
        self.assertIn('quantity', ctx.exception.message_dict)

        # Estoque permanece intacto
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_venda_exatamente_igual_ao_estoque_e_aceita(self):
        sale = Sale.objects.create(
            product=self.product, quantity=5, total_price='499.50',
            company=self.company, customer=self.customer,
        )
        sale.product.refresh_from_db()
        self.assertEqual(sale.product.stock, 0)

    def test_venda_valida_decrementa_estoque_e_soma_revenue(self):
        Sale.objects.create(
            product=self.product, quantity=2, total_price='199.80',
            company=self.company, customer=self.customer,
        )
        self.product.refresh_from_db()
        self.company.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(str(self.company.revenue), '199.80')

    def test_multiplas_vendas_acumulam_faturamento(self):
        Sale.objects.create(
            product=self.product, quantity=1, total_price='99.90',
            company=self.company, customer=self.customer,
        )
        Sale.objects.create(
            product=self.product, quantity=1, total_price='99.90',
            company=self.company, customer=self.customer,
        )
        Sale.objects.create(
            product=self.product, quantity=1, total_price='99.90',
            company=self.company, customer=self.customer,
        )
        self.product.refresh_from_db()
        self.company.refresh_from_db()
        self.assertEqual(self.product.stock, 2)
        self.assertEqual(str(self.company.revenue), '299.70')


class CustomerUniqueConstraintTests(TestCase):
    """Testes da constraint de email único por empresa."""

    def setUp(self):
        self.user_a = User.objects.create_user(username='owner_a', password='Senha@123')
        self.user_b = User.objects.create_user(username='owner_b', password='Senha@123')
        self.company_a = Company.objects.create(
            name='Empresa A', email='a@example.com', owner=self.user_a
        )
        self.company_b = Company.objects.create(
            name='Empresa B', email='b@example.com', owner=self.user_b
        )

    def test_emails_iguais_em_empresas_diferentes_sao_permitidos(self):
        Customer.objects.create(
            name='Maria', email='cliente@example.com', company=self.company_a
        )
        Customer.objects.create(
            name='Maria', email='cliente@example.com', company=self.company_b
        )
        self.assertEqual(Customer.objects.filter(email='cliente@example.com').count(), 2)

    def test_email_duplicado_na_mesma_empresa_falha(self):
        Customer.objects.create(
            name='João', email='joao@example.com', company=self.company_a
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Customer.objects.create(
                    name='João 2', email='joao@example.com', company=self.company_a
                )