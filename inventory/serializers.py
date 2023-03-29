"""
Serializers for the inventory app.
"""
from rest_framework import serializers
from .models import Category, Brand, ProductAttribute, ProductAttributeValue, Product


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


class ProductSerializer(serializers.ModelSerializer):
    """serializer for the product model."""
    brand = BrandSerializer()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'brand'
        ]
        read_only = True


class ProductDetailSerializer(serializers.ModelSerializer):
    """serializer for the product details."""
    brand = BrandSerializer()
    categories = SimpleCategorySerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'categories',
            'brand',
            'description',
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
