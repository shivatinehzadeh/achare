import datetime

import pytz
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import gettext_lazy as _

from achare.settings import read_env
from base.check_lock import wrong_data_function, get_client_ip, lock_time
from base.models import UserAccount, PhoneNumberCheck
from base.otp_handler import OTPHandler
from modules.phone_authenticate.serializers import PhoneSerializer, VerifyOtpSerializer


# Create your views here.


class PhoneAuthenticateView(APIView):
    serializer_class = PhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile_no = serializer.data['phone_number']
        user_ip = get_client_ip(request)
        phone_check_query = PhoneNumberCheck.objects.get_or_create(phone_number=mobile_no, user_ip=user_ip)
        if phone_check_query[0].is_lock:
            check_lock = lock_time(phone_check_query[0])
            if not check_lock:
                return Response(
                    {
                        "message": _(
                            f"This phone number is lock until {phone_check_query[0].lock_until.strftime('%H:%M:%S')}")
                    },
                    status=status.HTTP_423_LOCKED)

        return Response(
            {
                'phone_number': phone_check_query[0].phone_number,
                'registration_status': phone_check_query[0].registration_status
            },
            status=status.HTTP_200_OK
        )


class OTPView(GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = PhoneSerializer

    def get_serializer_class(self):
        if self.action == 'send_otp_request':
            return PhoneSerializer
        else:
            return VerifyOtpSerializer

    @action(methods=['POST'], detail=False)
    def send_otp_request(self, request):
        serialized_data = self.get_serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        received_data = serialized_data.validated_data
        phone_number = received_data['phone_number']
        otp = OTPHandler(mobile_no=phone_number)
        sms_text = _("OTP is : {}")
        otp_message = otp.send_otp(sms_text=sms_text)
        # I send otp as response because we don't have sms service for this task
        return Response(_(f"OTP sent, otp is :{otp_message}", ), status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def verify_otp_request(self, request):
        serialized_data = self.get_serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        received_data = serialized_data.validated_data
        phone_number = received_data['phone_number']
        otp_string = received_data['otp_string']
        try:
            get_phone_check_query = PhoneNumberCheck.objects.get(phone_number=phone_number)
            if get_phone_check_query.is_lock:
                check_lock = lock_time(get_phone_check_query)
                if not check_lock:
                    return Response(
                        {
                            "message": _(
                                f"This phone number is lock until {get_phone_check_query.lock_until.strftime('%H:%M:%S')}")
                        },
                        status=status.HTTP_423_LOCKED)
            if get_phone_check_query.registration_status:
                raise ValidationError({'message': _("you registered in the past")}, code=status.HTTP_400_BAD_REQUEST)
        except PhoneNumberCheck.DoesNotExist:
            raise ValidationError({'message': _("phone number is not valid")}, code=status.HTTP_400_BAD_REQUEST)
        otp = OTPHandler(mobile_no=phone_number)
        otp_verify = otp.verify_otp(otp_string)
        if otp_verify:
            response = {
                'detail': _(f"otp string is correct"),
                'phone_numer': phone_number}
            return Response(response, status=status.HTTP_200_OK)
        else:
            wrong_data_function(query=get_phone_check_query, request=request, user_ip_wrong=True)
            raise ValidationError({'message':_("OTP is Invalid")}, code=status.HTTP_400_BAD_REQUEST)
