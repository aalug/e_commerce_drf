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
