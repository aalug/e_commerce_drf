from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from inventory.models import Product, ProductAttributeValue, ProductAttribute, Category, Brand


@registry.register_document
class ProductDocument(Document):
    """Document for the product object."""
    categories = fields.TextField(attr='categories_indexing')
    attributes = fields.TextField(attr='attribute_values_indexing')
    brand = fields.TextField(attr='brand_indexing')

    class Index:
        name = 'product'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1
        }

    class Django:
        model = Product
        fields = [
            'id',
            'name',
            'description'
        ]
        related_models = [Category, ProductAttribute, ProductAttributeValue, Brand]

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(ProductDocument, self).get_queryset().select_related(
            'brand'
        )

