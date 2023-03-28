"""
URL mappings for the users API.
"""
from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('profile/', views.ManageUserView.as_view(), name='profile'),
    path('forgot-password/',
         views.ForgotPasswordView.as_view(),
         name='forgot-password'
         ),
    path('reset-password/<str:encoded_pk>/<str:token>/',
         views.ResetPasswordView.as_view(),
         name='reset-password'
         )
]
