"""
Tests for API calls that retrieve products.
"""
from _decimal import Decimal
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from inventory.models import Category, Product, Brand, ProductAttribute, ProductAttributeValue, ProductInventory

PRODUCTS_URL = reverse('inventory:products')
ATTRIBUTE_VALUES_URL = reverse('inventory:attribute-values')


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


def create_product_inventory(product, price='10.00', attribute_values=None):
    """Create and return a product inventory."""
    product_inventory = ProductInventory.objects.create(
        product=product,
        price=price
    )
    if attribute_values:
        for attr in attribute_values:
            product_inventory.attribute_values.add(attr)
    return product_inventory


def create_attribute_value(attr_name='test attr', attr_value='test value'):
    """Create and return a product attribute value."""
    product_attribute = ProductAttribute.objects.create(
        name=attr_name
    )
    return ProductAttributeValue.objects.create(
        product_attribute=product_attribute,
        value=attr_value
    )


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
        self.assertIn('all_attribute_values', results[0])
        self.assertIn('all_attribute_values', results[1])
        self.assertIn('price', results[0])
        self.assertIn('price', results[1])

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
        self.assertIn('product_inventories', res.data)
        self.assertIn('updated_at', res.data)

    def test_product_inventories_in_product_details(self):
        """Test product_inventories field in product details API endpoint."""
        ProductInventory.objects.create(
            product=self.product,
            price='10.50'
        )
        url = product_details_url(self.product.id)
        res = self.client.get(url)
        product_inventory = res.data['product_inventories'][0]

        self.assertIn('price', product_inventory)
        self.assertIn('stock', product_inventory)
        self.assertIn('attribute_values', product_inventory)

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

    def test_list_all_attribute_values(self):
        """Test listing all attribute values."""
        pa = ProductAttribute.objects.create(name='color')
        ProductAttributeValue.objects.create(
            product_attribute=pa,
            value='red'
        )
        ProductAttributeValue.objects.create(
            product_attribute=pa,
            value='blue'
        )
        res = self.client.get(ATTRIBUTE_VALUES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data['results']
        self.assertEqual(len(results), 2)
        self.assertTrue(
            (results[0]['value'] == 'red' and
             results[1]['value'] == 'blue') or
            (results[0]['value'] == 'blue' and
             results[1]['value'] == 'red')
        )

    def test_filter_products_by_attribute_values(self):
        """Test filtering products by attribute values."""
        attr_value = create_attribute_value()
        product_inventory = create_product_inventory(
            product=self.product,
            attribute_values=[attr_value]
        )
        other_product = create_product(name='other product')
        create_product_inventory(other_product)

        res = self.client.get(PRODUCTS_URL, {'attribute-values': attr_value.id})
        results = res.data['results']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.product.id)
        self.assertEqual(results[0]['price'], Decimal(product_inventory.price))
        self.assertEqual(results[0]['all_attribute_values'][0]['id'], attr_value.id)

    def test_filter_products_by_brand(self):
        """Test filtering products by brands."""
        create_product_inventory(
            product=self.product
        )
        brand_name = 'brand to test filter'
        new_brand = Brand.objects.create(
            name=brand_name
        )
        to_find_product = create_product(
            brand=new_brand,
            name='product to find'
        )
        create_product_inventory(to_find_product)

        res = self.client.get(PRODUCTS_URL, {'brand': new_brand.id})
        results = res.data['results']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], to_find_product.id)
        self.assertEqual(results[0]['brand']['id'], new_brand.id)
        self.assertEqual(results[0]['brand']['name'], new_brand.name)

    def test_filter_products_by_price_range(self):
        """Test filtering products by price range."""
        product_inventory = create_product_inventory(
            product=self.product,
            price='1000.00'
        )
        other_product = create_product(name='other product')
        other_product_inventory = create_product_inventory(product=other_product, price='5.00')

        res_1 = self.client.get(PRODUCTS_URL, {'price': '500,1100'})
        results_1 = res_1.data['results']

        self.assertEqual(res_1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_1), 1)
        self.assertEqual(results_1[0]['id'], self.product.id)
        self.assertEqual(results_1[0]['price'], Decimal(product_inventory.price))

        res_2 = self.client.get(PRODUCTS_URL, {'price': '0,10'})
        results_2 = res_2.data['results']

        self.assertEqual(res_1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_2), 1)
        self.assertEqual(results_2[0]['id'], other_product.id)
        self.assertEqual(results_2[0]['price'], Decimal(other_product_inventory.price))

    def test_filter_products_by_price_invalid_range(self):
        """Test error is raised if the price range is invalid."""
        res = self.client.get(PRODUCTS_URL, {'price': '100,5'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
