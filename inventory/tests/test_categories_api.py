"""
Tests for API calls that retrieve categories.
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from inventory.models import Category

MAIN_CATEGORIES_URL = reverse('inventory:main-categories')


def create_category(name='Test category', parent=None):
    """create and return a category."""
    return Category.objects.create(name=name, parent=parent)


def category_url(category_id):
    """Create and return a category url."""
    return reverse('inventory:category', args=[category_id])


class CategoryAPITests(TestCase):
    """Tests for the category related API calls."""

    def setUp(self):
        self.client = APIClient()

    def test_list_main_categories(self):
        """Test listing all main categories."""
        category = create_category()
        res = self.client.get(MAIN_CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'][0]['id'], category.id)
        self.assertEqual(res.data['results'][0]['name'], category.name)
        self.assertFalse(category.parent)

    def test_list_only_main_categories(self):
        """Test listing only main categories."""
        category_parent = create_category(name='parent')
        category_child = create_category(name='child', parent=category_parent)
        res = self.client.get(MAIN_CATEGORIES_URL)

        results = res.data['results']
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(category_parent.parent)
        self.assertEqual(results[0]['id'], category_parent.id)
        self.assertEqual(results[0]['name'], category_parent.name)
        for category in results:
            # None of the categories is the category_child
            self.assertNotEqual(category['id'], category_child.id)

    def test_retrieve_category(self):
        """Test retrieving a category is successful."""
        category_parent = create_category(name='parent')
        category_child = create_category(name='child', parent=category_parent)

        url = category_url(category_child.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], category_child.id)
        self.assertEqual(res.data['name'], category_child.name)

    def test_retrieve_category_children(self):
        """Test category is sent with its child categories."""
        category_parent = create_category(name='parent')
        category_child = create_category(name='child', parent=category_parent)
        category_grandchild = create_category(name='grandchild', parent=category_child)

        url = category_url(category_child.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['children'][0]['id'], category_grandchild.id)
        self.assertEqual(res.data['children'][0]['name'], category_grandchild.name)
        self.assertIn('children', res.data['children'][0])
