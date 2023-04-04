"""
Models for the inventory app.
"""
import datetime
import os
import random
import string
import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField


def image_file_path(instance, filename):
    """Generate file path for a new image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'products', filename)


class Category(MPTTModel):
    """Inventory Category table implemented with the MPTT."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('category name'),
        help_text=_('format: required, max-100'),
    )
    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('category safe URL')
    )
    is_active = models.BooleanField(default=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='children',
        null=True,
        blank=True,
        verbose_name=_('parent of category'),
        help_text=_('format: not required'),
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('product category')
        verbose_name_plural = _('product categories')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Create a slug and save the category."""
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Brand(models.Model):
    """Product brand table."""
    name = models.CharField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    """Product attribute table."""
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('product attribute name'),
        help_text=_('format: required, unique, max-255'),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('product attribute description'),
        help_text=_('format: not required'),
    )

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """Product attribute value table."""
    product_attribute = models.ForeignKey(
        ProductAttribute,
        related_name='product_attribute',
        on_delete=models.CASCADE,
    )
    value = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.product_attribute}: {self.value}'


class Product(models.Model):
    """Product details table."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    description = models.TextField()
    categories = TreeManyToManyField(Category)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def product_inventories(self):
        return ProductInventory.objects.filter(product=self)

    @property
    def price(self):
        """Return the price of the first product inventory associated with this product."""
        product_inventory = self.product_inventories.first()
        if product_inventory:
            return product_inventory.price

    @property
    def all_attribute_values(self):
        """Attribute values of all product inventories
           associated with this product."""
        attr_values = []
        for prod_inv in self.product_inventories:
            for attr in prod_inv.attribute_values.all():
                attr_values.append(attr)
        return attr_values

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Create a slug and a code and save the product."""
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class ProductInventory(models.Model):
    """Details for the product model."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventories'
    )
    code = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('unique product code')
    )
    attribute_values = models.ManyToManyField(
        ProductAttributeValue
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text=_('format: maximum price 9999.99')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def stock(self):
        """Return stock of this product inventory. """
        return Stock.objects.filter(product_inventory=self).first()

    def generate_product_code(self):
        """Generate a unique code for a product."""
        brand_initials = self.product.brand.name[:3]

        # Get the current time and date
        now = datetime.datetime.now()
        time = now.strftime('%Y%m%d%H%M%S')
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        # Combine the elements to create the product code
        return f'{code}-{self.product.name[-3:]}-{brand_initials}-{time}'.upper()

    def save(self, *args, **kwargs):
        """Save and generate unique code."""
        self.code = self.generate_product_code()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product} {self.id}'


class ProductImage(models.Model):
    """The product image table."""
    product_inventory = models.ForeignKey(
        ProductInventory,
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        verbose_name=_('product image'),
        upload_to=image_file_path
    )
    alt_text = models.CharField(
        max_length=255,
        verbose_name=_('alternative text')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')


class Stock(models.Model):
    """Stock table for the product inventory."""
    product_inventory = models.OneToOneField(
        ProductInventory,
        related_name='product_inventory',
        on_delete=models.CASCADE,
    )
    last_checked = models.DateTimeField(null=True, blank=True)
    units = models.PositiveIntegerField(
        default=0,
        verbose_name=_('units in stock')
    )
    units_sold = models.PositiveIntegerField(default=0)

    def calculate_units(self, n_of_sold_objects: int):
        """Calculate units and units_sold after selling object."""
        if self.units < n_of_sold_objects:
            raise ValueError(f'There is not enough units in stock - {self.units} but tried to sell {n_of_sold_objects}')
        self.units_sold += n_of_sold_objects
        self.units -= n_of_sold_objects
