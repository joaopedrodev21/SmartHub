from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.customers.models import Company, Customer
from apps.customers.permissions import IsCompanyOwner


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


class IsCompanyOwnerPermissionTests(TestCase):
    """Testes unitários da permission class IsCompanyOwner."""

    def setUp(self):
        self.owner = User.objects.create_user(username='dono', password='Senha@123')
        self.other = User.objects.create_user(username='outro', password='Senha@123')
        self.company = Company.objects.create(
            name='Minha Empresa', email='dono@example.com', owner=self.owner
        )
        self.factory = APIRequestFactory()
        self.permission = IsCompanyOwner()

    def _request_for(self, user):
        request = Request(self.factory.get('/'))
        request.user = user
        return request

    def test_dono_tem_permissao(self):
        self.assertTrue(self.permission.has_permission(self._request_for(self.owner), None))

    def test_usuario_sem_empresa_nao_tem_permissao(self):
        self.assertFalse(self.permission.has_permission(self._request_for(self.other), None))

    def test_anonimo_nao_tem_permissao(self):
        self.assertFalse(self.permission.has_permission(self._request_for(None), None))