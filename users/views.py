"""
Views for the users API.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.conf import settings
from django.utils.http import urlsafe_base64_encode

from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .models import UserProfile
from .serializers import UserProfileSerializer, AuthTokenSerializer, EmailSerializer, ResetPasswordSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user."""
    serializer_class = UserProfileSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserProfileSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user."""
        return UserProfile.objects.filter(
            user=self.request.user
        ).first()


class ForgotPasswordView(generics.GenericAPIView):
    """View for starting reset password process."""
    serializer_class = EmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        user = get_user_model().objects.filter(email=email).first()
        if user:
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = reverse('users:reset-password',
                                kwargs={
                                    'encoded_pk': encoded_pk,
                                    'token': token
                                })
            full_reset_url = f'{settings.HOST}{reset_url}'
            return Response({
                'message': 'Reset link was created.',
                'link': full_reset_url
            },
                status=status.HTTP_200_OK
            )
        return Response({
            'message': 'User wit this email does not exist.'
        },
            status=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordView(generics.GenericAPIView):
    """View for resetting a password."""
    serializer_class = ResetPasswordSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'kwargs': kwargs}
        )
        serializer.is_valid(raise_exception=True)
        return Response({
            'message': 'Password reset was successful.'
        },
            status=status.HTTP_200_OK
        )
