"""
Serializers for the users API.
"""
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers

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


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        required=True
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
