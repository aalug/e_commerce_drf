"""
Views for the inventory app.
"""
from rest_framework import generics

from .models import Product, Category, ProductAttributeValue
from .serializers import ProductSerializer, ProductDetailSerializer, CategorySerializer, ProductAttributeValueSerializer


class ListMainCategoriesAPIView(generics.ListAPIView):
    """List main categories - that do not have a parent category."""
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent=None)


class RetrieveCategoryAPIView(generics.RetrieveAPIView):
    """Retrieve category with children. Handles retrieving
       all categories except main ones. All children, grandchildren etc.
       use this view."""
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class ListProductsAPIView(generics.ListAPIView):
    """List products with general information."""
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class RetrieveProductAPIView(generics.RetrieveAPIView):
    """Retrieve product detail information."""
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()


class ListProductsByCategory(generics.ListAPIView):
    """List products by category."""
    serializer_class = ProductSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Product.objects.filter(
            categories__pk__in=[pk]
        )


class ListAllAttributeValues(generics.ListAPIView):
    """List all product attribute values. It's designed to be a list
       from which users can choose values to filter products."""
    serializer_class = ProductAttributeValueSerializer
    queryset = ProductAttributeValue.objects.all()
