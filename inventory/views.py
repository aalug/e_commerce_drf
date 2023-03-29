"""
Views for the inventory app.
"""
from rest_framework import generics

from . import serializers, models


class ListMainCategoriesAPIView(generics.ListAPIView):
    """List main categories - that do not have a parent category."""
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.filter(parent=None)


class RetrieveCategoryAPIView(generics.RetrieveAPIView):
    """Retrieve category with children. Handles retrieving
       all categories except main ones. All children, grandchildren etc.
       use this view."""
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()
