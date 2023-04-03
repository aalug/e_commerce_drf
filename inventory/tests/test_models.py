"""
Tests for the inventory app models.
"""
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from inventory.models import (Category,
                              Brand,
                              ProductAttribute,
                              ProductAttributeValue,
                              Product,
                              ProductInventory,
                              Stock)


class ModelTests(TestCase):
    """Tests for the inventory app models."""

    def test_create_category(self):
        category = Category.objects.create(
            name='test category'
        )
        self.assertTrue(
            Category.objects.filter(id=category.id).exists()
        )

    def test_category_slug(self):
        """Test that category slug is created on save."""
        category = Category.objects.create(name='test category slug')
        expected_slug = slugify(category.name)

        self.assertEqual(expected_slug, category.slug)

    def test_category_is_active(self):
        """Test category is active by default."""
        category = Category.objects.create(name='test')

        self.assertTrue(category.is_active)

    def test_category_parent(self):
        """Test category relation parent-child is created correctly. """
        parent_category = Category.objects.create(name='Parent Category')
        child_category = Category.objects.create(
            name='Child Category',
            parent=parent_category
        )
        expected_parent = child_category.parent

        self.assertEqual(expected_parent, parent_category)

    def test_category_order_insertion_by(self):
        """Test order_insertion_by of the MPTTMeta class."""
        parent_category = Category.objects.create(name='Parent Category')
        child_category_1 = Category.objects.create(
            name='Child Category 1',
            parent=parent_category
        )
        child_category_2 = Category.objects.create(
            name='Child Category 2',
            parent=parent_category
        )
        child_category_3 = Category.objects.create(
            name='Child Category 3',
            parent=parent_category
        )
        expected_children_order = [child_category_1, child_category_2, child_category_3]

        self.assertEqual(list(parent_category.children.all()), expected_children_order)

    def test_category_unique_slug(self):
        """Test that creating a category with a slug that already
           exists raises an exception."""
        Category.objects.create(name='Test Category 1', slug='test-category')

        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Test Category 2', slug='test-category')

    def test_category_unique_name(self):
        """Test that creating a category with a name that already
           exists raises an exception."""
        Category.objects.create(name='Test Category')

        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Test Category')

    def test_create_brand(self):
        """Test creating a brand object is successful."""
        brand = Brand.objects.create(name='test brand')

        self.assertTrue(
            Brand.objects.filter(id=brand.id).exists()
        )
        self.assertEqual(str(brand), brand.name)

    def test_brand_unique_name(self):
        """Test that creating a brand with a name that already
           exists raises an exception."""
        Brand.objects.create(name='test brand')

        with self.assertRaises(IntegrityError):
            Brand.objects.create(name='test brand')

    def test_create_product_attribute(self):
        """Test creating a product attribute is successful."""
        product_attr = ProductAttribute.objects.create(
            name='product attr',
            description='test description'
        )

        self.assertTrue(
            ProductAttribute.objects.filter(id=product_attr.id).exists()
        )
        self.assertTrue(str(product_attr), product_attr.name)

    def test_product_attribute_no_description_necessary(self):
        """Test that the description field is not required to create a product attribute."""
        product_attr = ProductAttribute.objects.create(
            name='product attr'
        )
        self.assertTrue(
            ProductAttribute.objects.filter(id=product_attr.id).exists()
        )

    def test_create_product_attribute_value(self):
        """Test creating a product attribute value is successful."""
        product_attr = ProductAttribute.objects.create(
            name='color'
        )
        product_attr_value = ProductAttributeValue.objects.create(
            product_attribute=product_attr,
            value='blue'
        )

        self.assertTrue(
            ProductAttributeValue.objects.filter(id=product_attr_value.id).exists()
        )

    def test_create_product(self):
        """Test creating a product is successful."""
        brand = Brand.objects.create(name='apple')
        product = Product.objects.create(
            name='macbook pro',
            description='apple computer',
            brand=brand
        )

        self.assertTrue(
            Product.objects.filter(id=product.id).exists()
        )
        self.assertEqual(product.brand, brand)
        self.assertEqual(str(product), product.name)

    def test_product_category(self):
        """Test product category field is set correctly."""
        category = Category.objects.create(name='clothes')
        brand = Brand.objects.create(name='brand')
        product = Product.objects.create(
            name='shirt',
            description='shirt',
            brand=brand
        )
        product.categories.add(category)

        self.assertIn(category, product.categories.all())

    def test_product_slug(self):
        """Test that product slug is created on save."""
        brand = Brand.objects.create(name='test brand')
        product = Product.objects.create(
            name='test product slug',
            description='test description',
            brand=brand
        )
        expected_slug = slugify(product.name)

        self.assertEqual(expected_slug, product.slug)

    def test_product_inventory(self):
        """Test creating a product inventory."""
        brand = Brand.objects.create(name='test brand')
        product = Product.objects.create(
            name='test product',
            description='test description',
            brand=brand
        )
        product_inventory = ProductInventory.objects.create(
            product=product,
            price='12.20'
        )

        self.assertTrue(
            ProductInventory.objects.filter(id=product_inventory.id).exists()
        )

    def test_product_inventory_code(self):
        """Test code is generated on save."""
        brand = Brand.objects.create(name='test brand')
        product = Product.objects.create(
            name='test product',
            description='test description',
            brand=brand
        )
        product_inventory = ProductInventory.objects.create(
            product=product,
            price='50.50'
        )
        product_inventory.save()
        first_part_patters = '^[A-Z0-9]{7}'
        time_pattern = '\d{14}'
        pattern = fr'{first_part_patters}-{product.name[-3:].upper()}-{product.brand.name[:3].upper()}-{time_pattern}'

        self.assertRegex(product_inventory.code, pattern)

    def test_create_stock(self):
        """Test creating a stock object is successful."""
        brand = Brand.objects.create(name='test brand')
        product = Product.objects.create(
            name='test product',
            description='test description',
            brand=brand
        )
        product_inventory = ProductInventory.objects.create(
            product=product,
            price='50.50'
        )
        stock = Stock.objects.create(
            product_inventory=product_inventory
        )

        self.assertTrue(
            Stock.objects.filter(id=stock.id).exists()
        )

    def test_stock_calculate_units(self):
        """Test calculate_units method of the stock model."""
        brand = Brand.objects.create(name='test brand')
        product = Product.objects.create(
            name='test product',
            description='test description',
            brand=brand
        )
        product_inventory = ProductInventory.objects.create(
            product=product,
            price='50.50'
        )
        stock = Stock.objects.create(
            product_inventory=product_inventory,
            units=10
        )
        stock.calculate_units(6)

        self.assertEqual(stock.units, 4)
        self.assertEqual(stock.units_sold, 6)

    def test_stock_calculate_units_not_enough_units(self):
        """Test calculate_units method raises exception
           if there is not enough units in stock."""
        brand = Brand.objects.create(name='test')
        product = Product.objects.create(
            name='test',
            description='description',
            brand=brand
        )
        product_inventory = ProductInventory.objects.create(
            product=product,
            price='5.10'
        )
        stock = Stock.objects.create(
            product_inventory=product_inventory,
            units=10
        )

        with self.assertRaises(ValueError):
            stock.calculate_units(50)

    def test_product_inventory_stock_property(self):
        """Test stock property of the product inventory."""
        brand = Brand.objects.create(name='test')
        product = Product.objects.create(
            name='test',
            description='description',
            brand=brand
        )
        product_inventory = ProductInventory.objects.create(
            product=product,
            price='5.10'
        )
        stock = Stock.objects.create(
            product_inventory=product_inventory,
            units=10
        )

        self.assertEqual(product_inventory.stock, stock)
