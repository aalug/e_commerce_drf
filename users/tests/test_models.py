"""
Tests for the users app models.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from users.models import UserProfile


class UserModelsTests(TestCase):
    """Test for the User and UserProfile model."""

    def test_create_user_with_email(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='password123'
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='password123'
            )

    def test_new_user_with_too_short_password_raises_error(self):
        """Test that creating a user with too short password raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(password='12345', email='test@example.com')

    def test_new_user_with_6_chars_password_success(self):
        """Test that creating a user with a password 6 characters
           does not raise a ValueError."""
        email = 'user@example.com'
        get_user_model().objects.create_user(
            email=email,
            password='123456'
        )
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertTrue(
            get_user_model().objects.filter(email=email).exists()
        )

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_user_profile_success(self):
        """Test creating a user profile is successful."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='password123'
        )
        user_profile = UserProfile.objects.create(
            user=user
        )
        self.assertEqual(str(user_profile), str(user))

