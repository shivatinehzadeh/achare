from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
BASE_API_PATH = ''
urlpatterns = [
    path("admin/", admin.site.urls),
    path(BASE_API_PATH, include('modules.phone_authenticate.urls'), ),
    path(BASE_API_PATH, include('modules.register.urls')),
    path(BASE_API_PATH, include('modules.login.urls'))
]
