"""
Django command to create fake products and populate the database with them.
"""
import random

from django.db import IntegrityError
from django.core.management import BaseCommand

from faker import Faker

from inventory.models import Category, Brand, Product


class Command(BaseCommand):
    """Django command to populate the database with products."""

    def handle(self, *args, **options):
        fake = Faker()
        brands = Brand.objects.all()
        all_categories = Category.objects.all()

        for _ in range(150):
            tree = random.randint(1, 3)
            category = random.choice(
                all_categories.filter(tree_id=tree).filter(level=2)
            )

            # Title
            num_words = random.randint(1, 4)
            book_title = fake.sentence(nb_words=num_words, variable_nb_words=True, ext_word_list=None)

            # Description
            num_sentences = random.randint(4, 6)
            book_description = fake.paragraphs(nb=num_sentences, ext_word_list=None)

            try:
                product = Product.objects.create(
                    name=book_title,
                    description=' '.join(book_description),
                    brand=random.choice(brands)
                )
                product.categories.add(
                    category,
                    category.parent,
                    category.parent.parent
                )
                product.save()
            except IntegrityError:
                # It can happen if the title already exists.
                # But chances are so small, there is no need to handle this error
                # product just will not be created.
                pass

