"""Add all API routes."""
from django.urls import path, include
from rest_framework import routers

from .views import LoginViewSet

router = routers.DefaultRouter(trailing_slash=True)

router.register(r'', LoginViewSet, basename='login')

urlpatterns = [
    path('', include(router.urls)),
]
