import datetime

import pytz
from rest_framework import status
from rest_framework.response import Response

from achare.settings import read_env
from django.utils.translation import gettext_lazy as _


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def wrong_data_function(query, request, user_ip_wrong=None, password_wrong=None):
    if user_ip_wrong:
        if get_client_ip(request) == query.user_ip:
            if query.user_ip_wrong_count:
                query.user_ip_wrong_count += 1
            else:
                query.user_ip_wrong_count = 1
    else:
        query.user_ip = get_client_ip(request)
        query.user_ip_wrong_count = 1
    if password_wrong:
        if query.wrong_password_count:
            query.wrong_password_count += 1
        else:
            query.wrong_password_count = 1
    if query.user_ip_wrong_count == int(read_env("MAX_TRY")) or query.wrong_password_count == int(read_env("MAX_TRY")):
        query.is_lock = True
        query.lock_until = datetime.datetime.now() + datetime.timedelta(hours=1)
    query.save()


def lock_time(query):
    utc = pytz.UTC
    if datetime.datetime.now().replace(tzinfo=utc) > query.lock_until.replace(tzinfo=utc):
        query.is_lock = False
        query.lock_until = None
        query.wrong_password_count = None
        query.user_ip_wrong_count = None
        query.save()
        return True
    else:
        return False

