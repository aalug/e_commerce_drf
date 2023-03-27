"""
Tests for the users API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from users.models import UserProfile

CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')
PROFILE_URL = reverse('users:profile')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public (that do not require authentication)
       features of the users API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Test creating a user is successful."""
        payload = {
            'user': {
                'email': 'user@example.com',
                'password': 'password123'
            },
            'first_name': 'Joe'
        }
        res = self.client.post(CREATE_USER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['user']['email'])
        self.assertTrue(user.check_password(payload['user']['password']))

        # Check that the API is secure and does not send password in plain text in response
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error is returned if user with email exists."""
        details = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        create_user(**details)
        res = self.client.post(CREATE_USER_URL, {'user': {**details}}, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'user': {
                'email': 'u@example.com',
                'password': '123'
            }
        }
        res = self.client.post(CREATE_USER_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['user']['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        payload = {
            'email': 'user@example.com',
            'password': 'password123'
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_bad_credentials(self):
        """Test return error if credentials are invalid."""

        user = create_user(
            email='user@example.com',
            password='password'
        )

        payload = {'email': user.email, 'password': 'wrong_password'}
        res = self.client.post(TOKEN_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_email_not_found(self):
        """Test returns error if the user with given email cannot be found."""
        payload = {'email': 'email@example.com', 'password': 'password123'}
        res = self.client.post(TOKEN_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required to get to the users profile."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_unauthorized(self):
        """Test authentication is required to update the users profile."""
        res = self.client.patch(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='password123'
        )
        UserProfile.objects.create(
            user=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile(self):
        """Test retrieving a profile for logged in user is successful."""
        res = self.client.get(PROFILE_URL)
        user = res.data['user']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(user['email'], self.user.email)
        self.assertIn('first_name', res.data)
        self.assertIn('last_name', res.data)
        self.assertIn('address', res.data)
        self.assertIn('country', res.data)
        self.assertIn('city', res.data)
        self.assertIn('zip_code', res.data)

    def test_post_profile_not_allowed(self):
        """Test POST is not allowed for the 'profile' endpoint."""
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_password(self):
        """Test updating the user password."""
        payload = {'user': {'password': 'new_password'}}
        res = self.client.patch(PROFILE_URL, payload, format='json')

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['user']['password']))

    def test_update_email_not_allowed(self):
        """Test that updating an email is not allowed."""
        payload = {'user': {'email': 'new_email@example.com'}}
        res = self.client.patch(PROFILE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile(self):
        """Test updating profile information is successful."""
        payload = {
            'first_name': 'John',
            'last_name': 'Test',
            'address': 'some address 12/3',
            'country': 'Poland',
            'city': 'My city',
            'zip_code': '12-345'
        }
        res = self.client.patch(PROFILE_URL, payload, format='json')
        profile = UserProfile.objects.filter(user=self.user).first()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.first_name, payload['first_name'])
        self.assertEqual(profile.last_name, payload['last_name'])
        self.assertEqual(profile.address, payload['address'])
        self.assertEqual(profile.country, payload['country'])
        self.assertEqual(profile.city, payload['city'])
        self.assertEqual(profile.zip_code, payload['zip_code'])
