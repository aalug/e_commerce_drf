"""
Serializers for the inventory app.
"""
from rest_framework import serializers
from . import models


class ChildCategorySerializer(serializers.ModelSerializer):
    """Serializer for the child of category model."""

    class Meta:
        model = models.Category
        fields = ['id', 'name', 'slug', 'children', 'is_active']
        read_only = True


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    children = ChildCategorySerializer(many=True)

    class Meta:
        model = models.Category
        fields = ['id', 'name', 'slug', 'children', 'is_active']
        read_only = True

