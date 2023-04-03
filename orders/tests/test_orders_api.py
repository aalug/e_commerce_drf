"""
Tests for orders related API calls..
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from inventory.models import Product, Brand, ProductInventory
from orders.models import Order

ORDERS_URL = reverse('orders:orders')


class PublicOrdersAPITests(TestCase):
    """Tests for the orders related API calls that
       do not require authentication."""

    def setUp(self):
        self.client = APIClient()

    def test_create_order_no_auth_not_allowed(self):
        """Test that creating an order without auth is not allowed."""
        res = self.client.post(ORDERS_URL, {})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders_no_auth_not_allowed(self):
        """Test that getting orders without auth is not allowed."""
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOrdersAPITests(TestCase):
    """Tests for the orders related API calls that
       do require authentication."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='customer@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)
        self.brand = Brand.objects.create(name='testBrand')
        self.product = Product.objects.create(
            name='test product',
            brand=self.brand
        )
        self.product_inventory_1 = ProductInventory.objects.create(
            product=self.product,
            price='10.00'
        )
        self.product_inventory_2 = ProductInventory.objects.create(
            product=self.product,
            price='15.00'
        )

    def test_create_order(self):
        """Test creating a new order is successful."""
        payload = {
            'products': [
                self.product_inventory_1.id,
                self.product_inventory_2.id
            ],
            'customer_first_name': 'Adam',
            'customer_last_name': 'Mada',
            'customer_address': 'main st. 12/3',
            'customer_country': 'USA',
            'customer_city': 'Boston',
            'customer_zip_code': '12-345'
        }
        res = self.client.post(ORDERS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(id=res.data['id']).exists())

    def test_create_order_no_products_error(self):
        """Test creating a new order without products raises an error."""
        payload = {
            'products': [],
            'customer_first_name': 'Adam',
            'customer_last_name': 'Mada',
            'customer_address': 'main st. 12/3',
            'customer_country': 'USA',
            'customer_city': 'Boston',
            'customer_zip_code': '12-345'
        }
        res = self.client.post(ORDERS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders(self):
        """Test listing users orders."""
        order = Order.objects.create(
            customer=self.user,
            customer_first_name='Joe',
            customer_last_name='Eoj',
            customer_email=self.user.email,
            customer_address='some street 12/3',
            customer_country='Poland',
            customer_city='Poznan',
            customer_zip_code='12-345'
        )
        order.products.add(
            self.product_inventory_1
        )
        res = self.client.get(ORDERS_URL)

        results = res.data['results']
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(results[0]['id'], order.id)
