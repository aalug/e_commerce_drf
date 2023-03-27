"""
Views for the users API.
"""
from rest_framework import generics

from .serializers import UserProfileSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user."""
    serializer_class = UserProfileSerializer
