"""
Django command to create fake product inventories and populate the database with them.
"""
import random

from django.core.management import BaseCommand

from inventory.models import Product, ProductInventory, ProductAttributeValue, ProductAttribute


class Command(BaseCommand):
    """Django command to populate the database with product inventories."""

    def handle(self, *args, **options):
        products = Product.objects.all()
        formats = ProductAttributeValue.objects.filter(product_attribute__name='Format')
        all_attrs = ProductAttribute.objects.all()
        author_attr = all_attrs.filter(name='Author').first()
        all_attrs = all_attrs.exclude(pk=author_attr.pk)

        for product in products:
            rand_attrs = random.sample(list(all_attrs), 3)
            rand_price = round(random.uniform(8, 25), 2)
            n = random.randint(1, 3)
            rand_formats = random.sample(list(formats), n)

            attr_values = []
            for attr in rand_attrs:
                pav = random.choice(ProductAttributeValue.objects.filter(product_attribute=attr))
                attr_values.append(pav)

            for formt in rand_formats:
                price = round(rand_price * random.uniform(0.8, 1.2), 2)
                product_inventory = ProductInventory.objects.create(
                    product=product,
                    price=str(price)
                )
                product_inventory.attribute_values.add(
                    formt,
                    *attr_values
                )
                product_inventory.save()
