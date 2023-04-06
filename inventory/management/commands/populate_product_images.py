"""
Django command to create fake product images and populate the database with them.
"""
import requests

from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import BaseCommand

from faker import Faker

from inventory.models import ProductInventory, ProductImage


class Command(BaseCommand):
    """Django command to populate the database with product images."""

    def handle(self, *args, **options):
        fake = Faker()
        all_product_inventories = ProductInventory.objects.all()

        for product_inventory in all_product_inventories:
            # Get an image
            img_url = fake.image_url(width=600, height=600)
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content)).convert('RGB')

            # Convert the image to the JPEG format
            img_io = BytesIO()
            img.save(img_io, format='JPEG')
            prod_img = SimpleUploadedFile(
                name='image.jpg',
                content=img_io.getvalue(),
                content_type='image/jpeg'
            )

            product_image = ProductImage.objects.create(
                product_inventory=product_inventory,
                image=prod_img,
                alt_text=f'{product_inventory} image.'
            )
            product_image.save()

