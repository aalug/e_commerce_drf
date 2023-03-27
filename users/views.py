"""
Views for the users API.
"""
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserProfileSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user."""
    serializer_class = UserProfileSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
