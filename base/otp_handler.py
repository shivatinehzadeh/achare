import base64
import logging
import os
import threading

import pyotp
from django.core.cache import caches, cache
from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import ValidationError
from achare.settings import read_env
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('OTP')


class OTPHandler(object):

    def __init__(self, mobile_no, cache_name='otp'):
        self.mobile_no = mobile_no
        self.cache = caches[cache_name]

    @staticmethod
    def generate_key(raw_str):
        return str(raw_str) + str(datetime.date(datetime.now())) + read_env('OTP_SECRET_KEY')

    def send_otp(self, sms_text="{}"):
        logger.info(f"*********** start send_otp *************")
        guid = pyotp.random_base32()
        raw_str = str(self.mobile_no)
        old_guid = self.cache.get(raw_str)
        logger.info(f"*********** response redis : {old_guid} *************")
        if old_guid:
            raise ValidationError({'message': _('Less than 90 seconds have passed since the previous OTP was sent')},
                                  code=status.HTTP_400_BAD_REQUEST)
        key = base64.b32encode((self.generate_key(raw_str=raw_str) + guid).encode())
        otp = pyotp.TOTP(key, interval=90)
        otp_6_digits = otp.now()
        logger.info(f"*********** otp is {otp_6_digits} *************")
        self.cache.set(raw_str, guid, 90)
        logger.info(f"*********** after cache set *************")
        # send sms
        return otp_6_digits

    def verify_otp(self, otp_string):
        raw_str = str(self.mobile_no)
        guid = self.cache.get(raw_str)
        if not guid:
            return False
        key = base64.b32encode((self.generate_key(raw_str) + guid).encode())
        otp = pyotp.TOTP(key, interval=90)
        otp_bool = otp.verify(otp_string, valid_window=1)
        if otp_bool:
            self.cache.delete(raw_str)
            return True
        else:
            return False
