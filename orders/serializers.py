"""
Serializers for the orders' app.
"""
from rest_framework import serializers

from inventory.models import ProductInventory, Product, ProductAttribute, ProductAttributeValue
from inventory.serializers import BrandSerializer
from .models import Order


class ProductSerializer(serializers.ModelSerializer):
    """serializer for the product model."""
    brand = BrandSerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'brand', ]
        read_only = True


class ProductAttributeSerializer(serializers.ModelSerializer):
    """Serializer for the product attribute model."""

    class Meta:
        model = ProductAttribute
        fields = ['name']
        read_only = True


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for the product attribute value model."""
    product_attribute = ProductAttributeSerializer()

    class Meta:
        model = ProductAttributeValue
        fields = ['product_attribute', 'value']
        read_only = True


class ProductInventorySerializer(serializers.ModelSerializer):
    """Serializer for the product inventory."""
    attribute_values = ProductAttributeValueSerializer(many=True)
    product = ProductSerializer()

    class Meta:
        model = ProductInventory
        fields = ['product', 'attribute_values', 'price']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the order model."""

    class Meta:
        model = Order
        fields = [
            'id',
            'products',
            'customer_first_name',
            'customer_last_name',
            'customer_address',
            'customer_country',
            'customer_city',
            'customer_zip_code'
        ]
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        """Create a new order. Checks if the request contains
           products, if not - raises an Error."""
        products = validated_data.pop('products')
        if not products:
            raise serializers.ValidationError('The products list cannot be empty.')

        # Create the order
        order = Order.objects.create(**validated_data)

        # Add products to the order
        for product in products:
            order.products.add(product)

        return order


class GetOrderSerializer(OrderSerializer):
    """Serializer for getting order data. It has additional data,
       not needed to create an order (in `OrderSerializer`)."""
    products = ProductInventorySerializer(many=True)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + [
            'status',
            'customer_email',
            'total_price',
            'created_at'
        ]
        read_only = True
