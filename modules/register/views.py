from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from base.models import PersonInfo
from modules.register.serializers import PersonInfoSerializer


# Create your views here.

class RegisterViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = PersonInfo.objects.all()
    serializer_class = PersonInfoSerializer
