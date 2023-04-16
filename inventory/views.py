"""
Views for the inventory app.
"""
from _decimal import Decimal
from elasticsearch_dsl import Q
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

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
    """List products with general information. get_queryset method can
       handle filtering by category, brand, attribute values, price range and
       can handle searching for products which is done by using elastic search.
       Cache is set, so that SQL queries are not needed every time.
       The cache is set to 30 minutes."""
    serializer_class = ProductSerializer
    search_document = ProductDocument

    @staticmethod
    def _params_to_ints(param_array):
        """Convert a list of string IDs to a list of integers."""
        return [int(str_id) for str_id in param_array.split(',')]

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 30))
    def dispatch(self, *args, **kwargs):
        return super(ListProductsAPIView, self).dispatch(*args, **kwargs)

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
            queryset = queryset.filter(inventories__attribute_values__id__in=attr_ids).distinct()

        # Filter by brands
        if brand:
            brand_ids = self._params_to_ints(brand)
            queryset = queryset.filter(brand__id__in=brand_ids).distinct()

        # Filter by price range
        if price_range:
            price_range = price_range.split(',')
            if len(price_range) == 2:
                start_price, end_price = price_range
                try:
                    start_price = int(start_price)
                    end_price = int(end_price)
                except ValueError:
                    raise ValidationError(
                        'Invalid price range. The correct format is: int,int.'
                    )

                if start_price > end_price:
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

                # Get the intersection of products_ids and ids of products in the queryset
                queryset_ids = [q.id for q in queryset]
                ids = list(set(products_ids) & set(queryset_ids))

                queryset = Product.objects.filter(id__in=ids)

            except Exception as e:
                return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return queryset


class RetrieveProductAPIView(generics.RetrieveAPIView):
    """Retrieve product detail information."""
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()


class ListAllAttributeValues(generics.ListAPIView):
    """List all product attribute values. It's designed to be a list
       from which users can choose values to filter products.
       Cache is set, so that SQL queries are not needed every time.
       The cache is set to 60 minutes."""
    serializer_class = ProductAttributeValueSerializer
    queryset = ProductAttributeValue.objects.all()

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 60))
    def dispatch(self, *args, **kwargs):
        return super(ListAllAttributeValues, self).dispatch(*args, **kwargs)