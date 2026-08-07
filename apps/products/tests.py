from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from apps.customers.models import Company
from apps.products.models import Product


class ProductTenantIsolationTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='tenant_a', email='a@example.com', password='12345678')
        self.user_b = User.objects.create_user(username='tenant_b', email='b@example.com', password='12345678')

        self.company_a = Company.objects.create(name='Company A', email='a@company.com', owner=self.user_a)
        self.company_b = Company.objects.create(name='Company B', email='b@company.com', owner=self.user_b)

        self.product_a = Product.objects.create(
            name='Product A',
            description='A',
            price='10.00',
            stock=5,
            category='hardware',
            brand='Brand A',
            company=self.company_a,
        )
        self.product_b = Product.objects.create(
            name='Product B',
            description='B',
            price='20.00',
            stock=3,
            category='hardware',
            brand='Brand B',
            company=self.company_b,
        )

    def test_user_sees_only_products_from_own_company(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('products:product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product_a.name)
        self.assertNotContains(response, self.product_b.name)
