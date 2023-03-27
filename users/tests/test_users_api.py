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

