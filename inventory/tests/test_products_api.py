"""
Tests for API calls that retrieve products.
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from inventory.models import Category, Product, Brand

PRODUCTS_URL = reverse('inventory:products')


def create_category(name='Test category', parent=None):
    """create and return a category."""
    return Category.objects.create(name=name, parent=parent)


def create_product(brand=None, new_categories=None, **params):
    """Create and return a product."""
    if brand is None:
        brand = Brand.objects.all().first()
        if not brand:
            brand = Brand.objects.create(name='test brand')

    details = {
        'name': 'test product',
        'brand': brand,
        'description': 'test description',
    }
    details.update(params)
    product = Product.objects.create(**details)
    if new_categories is not None:
        for cat in new_categories:
            product.categories.add(cat.id)

    return product


def product_details_url(product_id):
    """Create and return a product details url."""
    return reverse('inventory:product-details', args=[product_id])


def products_by_category_url(category_id):
    """Create and return a product details url."""
    return reverse('inventory:products-by-category', args=[category_id])


class ProductsAPITests(TestCase):
    """Tests for the product related API calls."""

    def setUp(self):
        self.client = APIClient()
        self.parent_category = create_category(name='parent category')
        self.child_category = create_category(
            name='child category',
            parent=self.parent_category
        )
        self.product = create_product(
            new_categories=[self.child_category, self.parent_category]
        )

    def test_list_products(self):
        """Test listing products is successful."""
        new_product = create_product(name='new product')
        res = self.client.get(PRODUCTS_URL)
        results = res.data['results']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(results),
            Product.objects.all().count()
        )
        self.assertTrue(results[0]['name'] == self.product.name or
                        results[0]['name'] == new_product.name)
        self.assertTrue(results[0]['name'] == self.product.name or
                        results[0]['name'] == new_product.name)

    def test_retrieve_product_details(self):
        """Test retrieving product details is successful."""
        url = product_details_url(self.product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], self.product.id)
        self.assertEqual(res.data['name'], self.product.name)
        self.assertIn('slug', res.data)
        self.assertIn('categories', res.data)
        self.assertIn('brand', res.data)
        self.assertIn('description', res.data)
        self.assertIn('updated_at', res.data)

    def test_product_categories_sort(self):
        """Test categories are sorted by level in ascending order."""
        url = product_details_url(self.product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['categories'][0]['level'], 0)
        self.assertEqual(res.data['categories'][1]['level'], 1)

    def test_list_products_by_category(self):
        """Test list products by category."""
        category = create_category(
            'new category',
            parent=self.parent_category
        )
        product_1 = create_product(
            new_categories=[self.parent_category, self.child_category],
            name='product 1'
        )
        product_2 = create_product(
            new_categories=[self.parent_category, category],
            name='product 2'
        )

        url_1 = products_by_category_url(self.parent_category.id)
        res_1 = self.client.get(url_1)

        results_1 = sorted(res_1.data['results'], key=lambda p: p['id'])

        self.assertEqual(res_1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_1), 3)
        self.assertEqual(results_1[0]['id'], self.product.id)
        self.assertEqual(results_1[1]['id'], product_1.id)
        self.assertEqual(results_1[2]['id'], product_2.id)

        url_2 = products_by_category_url(self.child_category.id)
        res_2 = self.client.get(url_2)

        results_2 = sorted(res_2.data['results'], key=lambda p: p['id'])

        self.assertEqual(res_2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_2), 2)
        self.assertEqual(results_2[0]['id'], self.product.id)
        self.assertEqual(results_2[1]['id'], product_1.id)

        url_3 = products_by_category_url(category.id)
        res_3 = self.client.get(url_3)

        results_3 = res_3.data['results']

        self.assertEqual(res_3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_3), 1)
        self.assertEqual(results_3[0]['id'], product_2.id)
