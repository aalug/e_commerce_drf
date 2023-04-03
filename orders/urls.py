"""
URL mappings for the orders API.
"""
from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderAPIView.as_view(), name='orders'),
]
