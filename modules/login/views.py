import datetime

import jwt
import pytz
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from achare import settings
from base.check_lock import wrong_data_function, lock_time
from base.models import UserAccount, PhoneNumberCheck
from modules.login.serializers import UserSerializer


# Create your views here.

class LoginViewSet(GenericViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserSerializer

    @action(methods=['POST'], detail=False)
    def login(self, request):
        serialized_data = self.get_serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        phone_number = serialized_data.validated_data['phone_number']
        password = serialized_data.validated_data['password']
        try:
            get_user_query = UserAccount.objects.get(phone_register__phone_number=phone_number)
            if get_user_query.phone_register.is_lock:
                check_lock = lock_time(get_user_query.phone_register)
                if not check_lock:
                    return Response(
                        {
                            "message": _(
                                f"This phone number is lock until {get_user_query.phone_register.lock_until.strftime('%H:%M:%S')}")
                        },
                        status=status.HTTP_423_LOCKED)
            if not check_password(password, get_user_query.password):
                wrong_data_function(query=get_user_query.phone_register, request=request, password_wrong=True)
                raise ValidationError({'invalid': _("phone number or password is not valid")},
                                      code=status.HTTP_400_BAD_REQUEST)
            else:
                get_user_query.phone_register.is_lock = False
                get_user_query.phone_register.lock_until = None
                get_user_query.phone_register.wrong_password_count = None
                get_user_query.phone_register.user_ip_wrong_count = None
                get_user_query.phone_register.save()
                token = generate_token(get_user_query.id, settings.SECRET_KEY)
                return Response({'access_token': token}, status=status.HTTP_200_OK)

        except UserAccount.DoesNotExist:
            # wrong_data_function(query=get_user_query.phone_register, request=request, user_ip_wrong=True)
            raise ValidationError({'invalid': _("phone number or password is not valid")},
                                  code=status.HTTP_400_BAD_REQUEST)


def generate_token(user_id, secret_key):
    utc = pytz.UTC
    payload = {
        'user_id': user_id,
        'time': datetime.datetime.now().strftime('%Y%M%D')
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')
