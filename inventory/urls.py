"""
URL mappings for the inventory API.
"""
from django.urls import path

from . import views

app_name = 'inventory'
urlpatterns = [
    path('main-categories/', views.ListMainCategoriesAPIView.as_view(), name='main-categories'),
    path('categories/<int:pk>/', views.RetrieveCategoryAPIView.as_view(), name='category'),
    path('products/', views.ListProductsAPIView.as_view(), name='products'),
    path('products-by-category/<int:pk>/', views.ListProductsByCategory.as_view(), name='products-by-category'),
    path('products/<int:pk>/', views.RetrieveProductAPIView.as_view(), name='product-details'),
]

