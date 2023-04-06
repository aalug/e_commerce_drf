"""
Django command to create fake products and populate the database with them.
"""
import random
import string

from django.db import IntegrityError
from django.core.management import BaseCommand

from faker import Faker

from inventory.models import ProductAttribute, ProductAttributeValue


class Command(BaseCommand):
    """Django command to populate the database with categories, brands and products."""

    def handle(self, *args, **options):
        fake = Faker()

        # Create authors
        author_attr = ProductAttribute.objects.create(
            name='Author',
            description='Author of a book.'
        )
        for _ in range(10):
            try:
                pav = ProductAttributeValue.objects.create(
                    product_attribute=author_attr,
                    value=fake.name()
                )
                pav.save()
            except IntegrityError:
                pass

        for _ in range(10):
            initials = f'{random.choice(string.ascii_uppercase)}.{random.choice(string.ascii_uppercase)}.'
            try:
                pav = ProductAttributeValue.objects.create(
                    product_attribute=author_attr,
                    value=f'{initials}{fake.last_name()}'
                )
                pav.save()
            except IntegrityError:
                pass

        # Create format attribute
        format_attr = ProductAttribute.objects.create(
            name='Format',
            description='Book format.'
        )
        formats = [' Paperback', 'Hardcover', 'Audiobook', 'eBook']
        for f in formats:
            pav = ProductAttributeValue.objects.create(
                product_attribute=format_attr,
                value=f
            )
            pav.save()

        # Language attribute
        language_attr = ProductAttribute.objects.create(
            name='Language'
        )
        languages = ['English', 'Spanish', 'French', 'Polish', 'German', 'Italian']
        for lang in languages:
            pav = ProductAttributeValue.objects.create(
                product_attribute=language_attr,
                value=lang
            )
            pav.save()

        # Audience attribute
        audience_attr = ProductAttribute.objects.create(
            name='Audience'
        )
        audiences = ['Children', 'Young Adult', 'Adult']
        for a in audiences:
            pav = ProductAttributeValue.objects.create(
                product_attribute=audience_attr,
                value=a
            )
            pav.save()

        # Setting attribute
        setting_attr = ProductAttribute.objects.create(
            name='Setting'
        )
        settings = ['New York City', 'Hogwarts',
                    'Middle-earth', 'The Wild West'
                                    'The Moon', 'A deserted island',
                    'Mars', 'A medieval castle',
                    'A post-apocalyptic wasteland']
        for s in settings:
            pav = ProductAttributeValue.objects.create(
                product_attribute=setting_attr,
                value=s
            )
            pav.save()

        # Theme attribute
        theme_attr = ProductAttribute.objects.create(
            name='Theme'
        )
        themes = ['Love and Loss', 'Identity and Self-Discovery',
                  'Good vs. Evil', 'Betrayal and Revenge',
                  'War and Conflict', 'Hope and Despair',
                  'Family and Relationships', 'Justice and Injustice',
                  'Dreams and Reality', 'Redemption and Forgiveness']
        for t in themes:
            pav = ProductAttributeValue.objects.create(
                product_attribute=theme_attr,
                value=t
            )
            pav.save()

        # Award attribute
        award_attr = ProductAttribute.objects.create(
            name='Award'
        )
        awards = ['Pulitzer Prize', 'Man Booker Prize', 'National Book Award']
        for a in awards:
            pav = ProductAttributeValue.objects.create(
                product_attribute=award_attr,
                value=a
            )
            pav.save()
