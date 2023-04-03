"""
Test for the orders app models.
"""
from _decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from inventory.models import Product, Brand, ProductInventory
from orders.models import Order


class ModelTests(TestCase):
    """Tests for the orders app models."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='password123'
        )

    def test_create_order(self):
        """Test creating an order."""
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

        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(Order.objects.filter(id=order.id).count(), 1)

    def test_order_status(self):
        """Test order status."""
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

        self.assertEqual(order.status, Order.STATUS_CHOICES[0][0])

        order.status = 'C'
        self.assertEqual(order.status, Order.STATUS_CHOICES[1][0])

    def test_total_price_property(self):
        """Test total_price property of the Order model."""
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
        brand = Brand.objects.create(name='BRAND!')
        product = Product.objects.create(
            name='test product',
            brand=brand
        )
        price_1 = '10.00'
        product_inventory_1 = ProductInventory.objects.create(
            product=product,
            price=price_1
        )
        price_2 = '12.30'
        product_inventory_2 = ProductInventory.objects.create(
            product=product,
            price=price_2
        )
        order.products.add(product_inventory_1)
        order.products.add(product_inventory_2)

        self.assertEqual(order.total_price, Decimal('22.30'))
