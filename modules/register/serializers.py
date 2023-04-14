from django.contrib.auth.hashers import make_password
from rest_framework import serializers, status
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, NotFound

from base.models import PersonInfo, PhoneNumberCheck, UserAccount


class PersonInfoSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=11, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = PersonInfo
        fields = '__all__'
        read_only_fields = ['id', 'phone_register', 'user']

    def create(self, validated_data):
        try:
            phone_number = validated_data.pop('phone_number')
            get_phone_query = PhoneNumberCheck.objects.get(phone_number=phone_number)
            if get_phone_query.registration_status:
                raise serializers.ValidationError({'message': _('this phone number was registered in the past')},
                                                  code=status.HTTP_400_BAD_REQUEST)
        except PhoneNumberCheck.DoesNotExist:
            raise NotFound({'message': _("phone number is not valid")},
                           code=status.HTTP_404_NOT_FOUND)
        validated_data['phone_register'] = get_phone_query
        password = make_password(validated_data.pop('password'))
        create_user = UserAccount.objects.create(phone_register=get_phone_query, password=password)
        validated_data['user'] = create_user
        get_phone_query.registration_status = True
        get_phone_query.save()
        return super().create(validated_data)
