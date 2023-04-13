from rest_framework import serializers


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

class VerifyOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    otp_string = serializers.CharField(max_length=11)
