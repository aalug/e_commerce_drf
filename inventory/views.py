"""
Views for the inventory app.
"""
from _decimal import Decimal
from elasticsearch_dsl import Q
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .documents import ProductDocument
from .models import Product, Category, ProductAttributeValue
from .serializers import (ProductSerializer,
                          ProductDetailSerializer,
                          CategorySerializer,
                          ProductAttributeValueSerializer,
                          ProductSearchSerializer)


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
    search_document = ProductDocument

    @staticmethod
    def _params_to_ints(param_array):
        """Convert a list of string IDs to a list of integers."""
        return [int(str_id) for str_id in param_array.split(',')]

    def get_queryset(self):
        # Check if the category id was provided
        # if it was, filter by it
        category_pk = self.kwargs.get('pk')
        if category_pk:
            queryset = Product.objects.filter(
                categories__pk__in=[category_pk]
            )
        # else, set queryset to all products
        else:
            queryset = Product.objects.all()

        attribute_values = self.request.query_params.get('attribute-values')
        brand = self.request.query_params.get('brand')
        price_range = self.request.query_params.get('price')
        search_query = self.request.query_params.get('search')

        # Filter by attribute values
        if attribute_values:
            attr_ids = self._params_to_ints(attribute_values)
            queryset = queryset.filter(inventories__attribute_values__id__in=attr_ids)

        # Filter by brands
        if brand:
            brand_ids = self._params_to_ints(brand)
            queryset = queryset.filter(brand__id__in=brand_ids)

        # Filter by price range
        if price_range:
            price_range = price_range.split(',')
            if len(price_range) == 2:
                start_price, end_price = price_range
                if Decimal(start_price) > Decimal(end_price):
                    raise ValidationError(
                        'Invalid price range. The start price has to be lower than the end price.'
                    )
                queryset = queryset.filter(
                    inventories__price__range=(start_price, end_price)
                )

        # Search
        if search_query:
            try:
                q = Q(
                    'multi_match',
                    query=search_query,
                    fields=[
                        'name',
                        'description',
                        'categories',
                        'brand',
                        'attributes'
                    ],
                    fuzziness='auto',
                    minimum_should_match=1
                )
                search = ProductDocument.search().query(q).execute()
                # data is an array of dicts that contain products ids
                data = ProductSearchSerializer(search, many=True).data
                products_ids = [d['id'] for d in data]
                queryset = Product.objects.filter(id__in=products_ids)

            except Exception as e:
                return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return queryset


class RetrieveProductAPIView(generics.RetrieveAPIView):
    """Retrieve product detail information."""
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()


class ListAllAttributeValues(generics.ListAPIView):
    """List all product attribute values. It's designed to be a list
       from which users can choose values to filter products."""
    serializer_class = ProductAttributeValueSerializer
    queryset = ProductAttributeValue.objects.all()
