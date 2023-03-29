"""
URL mappings for the inventory API.
"""
from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path('main-categories/', views.ListMainCategoriesAPIView.as_view(), name='main-categories'),
    path('categories/<int:pk>/', views.RetrieveCategoryAPIView.as_view(), name='category'),
]
