"""
Django command to create stock and populate the database with them.
"""
import random

from django.core.management import BaseCommand

from inventory.models import Stock, ProductInventory


class Command(BaseCommand):
    """Django command to populate the database with stock objects."""

    def handle(self, *args, **options):
        all_product_inventories = ProductInventory.objects.all()
        for product_inventory in all_product_inventories:
            stock = Stock.objects.create(
                product_inventory=product_inventory,
                units=random.randint(0, 50),
                units_sold=random.randint(0, 50)
            )
            stock.save()
