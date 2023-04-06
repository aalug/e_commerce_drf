"""
Django command to create fake brands and populate the database with them.
"""
from django.core.management import BaseCommand

from inventory.models import Brand


class Command(BaseCommand):
    """Django command to populate the database with brands."""

    def handle(self, *args, **options):
        # list of random brand names
        brand_names = ['Bloom & Birch', 'Raven Press', 'Frost & Fable', 'Phoenix Books',
                       'Hawthorne House', 'Cedar & Sage', 'Willow Press', 'Siren Books',
                       'Redwood Publishing', 'Midnight Ink', 'Moonstone Books', 'Wildflower Press',
                       'Silk & Stone', 'Sunflower Books', 'Wren Publishing']

        for name in brand_names:
            brand = Brand.objects.create(name=name)
            brand.save()
