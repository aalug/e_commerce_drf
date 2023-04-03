"""
Views for the orders' app.
"""
from rest_framework import generics, authentication, permissions

from orders.models import Order
from orders.serializers import OrderSerializer, GetOrderSerializer


class OrderAPIView(generics.ListCreateAPIView):
    """APIView for creating and listing orders."""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.request.method == 'GET':
            return GetOrderSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        return serializer.save(
            customer=self.request.user,
            customer_email=self.request.user.email
        )

