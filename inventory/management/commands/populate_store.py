"""
Django command to populate the database with all models.
"""
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    """Django command to call all populating database commands."""

    def handle(self, *args, **options):
        call_command('makemigrations')
        call_command('migrate')

        call_command('loaddata', 'category_fixtures.json')
        call_command('populate_attributes')
        call_command('populate_brands')
        call_command('populate_products')
        call_command('populate_product_inventories')
        call_command('populate_stock')
        call_command('populate_product_images')

        self.stdout.write(self.style.SUCCESS('Objects created successfully.'))

