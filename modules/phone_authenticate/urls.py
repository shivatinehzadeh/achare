"""Add all API routes."""
from django.urls import path, include
from rest_framework import routers

from .views import OTPView, PhoneAuthenticateView

app_name = 'phone-authenticate'
router = routers.DefaultRouter(trailing_slash=True)

router.register(r'', OTPView, basename='otp')

urlpatterns = [
    path('', include(router.urls)),
    path('get_phone/', PhoneAuthenticateView.as_view(), name='get-phone')
]
