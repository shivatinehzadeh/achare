"""Add all API routes."""
from django.urls import path, include
from rest_framework import routers

from .views import OTPView,PhoneAuthenticateView

router = routers.DefaultRouter(trailing_slash=True)

router.register(r'', OTPView, basename='otp')
# router.register(r'login_history', LoginHistoryViewSet, basename='login')
# router.register(r'logout', LogoutGenericView, basename='Logout')

urlpatterns = [
    # path('account/', include(router.urls)),
    path('', include(router.urls)),
    path('get_phone/', PhoneAuthenticateView.as_view(), name='get_phone')
]
