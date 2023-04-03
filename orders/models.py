"""
Models for the orders' app.
"""
from django.conf import settings
from django.db import models

from inventory.models import ProductInventory


class Order(models.Model):
    """Order table."""
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('C', 'Confirmed'),
        ('D', 'Delivered'),
        ('R', 'Returned'),
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    products = models.ManyToManyField(ProductInventory)
    customer_first_name = models.CharField(max_length=255)
    customer_last_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_address = models.CharField(max_length=255)
    customer_country = models.CharField(max_length=255)
    customer_city = models.CharField(max_length=255)
    customer_zip_code = models.CharField(max_length=15)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        """Calculate total price of all products."""
        total = 0
        for product in self.products.all():
            total += product.price
        return total
