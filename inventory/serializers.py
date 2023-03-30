"""
Serializers for the inventory app.
"""
from rest_framework import serializers
from .models import Category, Brand, ProductAttribute, ProductAttributeValue, Product, ProductInventory, Stock


class ChildCategorySerializer(serializers.ModelSerializer):
    """Serializer for the child of category model."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'children', 'is_active']
        read_only = True


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    children = ChildCategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'children', 'is_active']
        read_only = True


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for the brand model."""

    class Meta:
        model = Brand
        fields = ['id', 'name']
        read_only = True


class SimpleCategorySerializer(serializers.ModelSerializer):
    """Simple serializer to handling category details needed by the ProductSerializer.
       It's designed help with listing categories of displayed product. User then can
       choose one of the categories and look for items that are associated with it."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'level']
        read_only = True


class ProductAttributeSerializer(serializers.ModelSerializer):
    """Serializer for the product attribute model."""

    class Meta:
        model = ProductAttribute
        fields = ['name', 'description']
        read_only = True


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for the product attribute value model."""
    product_attribute = ProductAttributeSerializer()

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'product_attribute', 'value']
        read_only = True


class StockSerializer(serializers.ModelSerializer):
    """Serializer for the stock model."""

    class Meta:
        model = Stock
        fields = ['units']
        read_only = True


class ProductInventorySerializer(serializers.ModelSerializer):
    """Serializer for the product inventory."""
    attribute_values = ProductAttributeValueSerializer(many=True)
    stock = StockSerializer()

    class Meta:
        model = ProductInventory
        fields = ['attribute_values', 'price', 'stock']


class ProductSerializer(serializers.ModelSerializer):
    """serializer for the product model."""
    brand = BrandSerializer()
    all_attribute_values = ProductAttributeValueSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'brand',
            'all_attribute_values'
        ]
        read_only = True


class ProductDetailSerializer(serializers.ModelSerializer):
    """serializer for the product details."""
    brand = BrandSerializer()
    categories = SimpleCategorySerializer(many=True)
    product_inventories = ProductInventorySerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'categories',
            'brand',
            'description',
            'product_inventories',
            'updated_at'
        ]
        read_only = True

    def to_representation(self, instance):
        """Overwrite the method to sort categories by level, so they are
           sorted from the most general to the lease general category."""
        response = super().to_representation(instance)
        response['categories'] = sorted(
            response['categories'],
            key=lambda c: c['level']
        )
        return response
