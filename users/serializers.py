"""
Serializers for the users API.
"""
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers, exceptions

from users.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'password')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True, 'min_length': 6}
        }


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the UserProfile object. It can be used to create a user
       with UserProfile and to update password and all profile information."""
    user = UserSerializer(required=True)

    class Meta:
        model = UserProfile
        fields = (
            'user',
            'first_name',
            'last_name',
            'address',
            'country',
            'city',
            'zip_code'
        )

    def create(self, validated_data):
        """Create a new user with encrypted password and UserProfile."""
        user_data = validated_data.pop('user')

        # Create the user object
        user = get_user_model().objects.create_user(
            email=user_data['email'],
            password=user_data['password']
        )

        # Create the user profile object
        profile = UserProfile.objects.create(
            user=user,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            address=validated_data.get('address', ''),
            country=validated_data.get('country', ''),
            city=validated_data.get('city', ''),
            zip_code=validated_data.get('zip_code', ''),
        )
        return profile

