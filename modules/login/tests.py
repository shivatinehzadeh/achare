from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import datetime

from base.models import UserAccount, PhoneNumberCheck, PersonInfo


class LoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        password = make_password('12345')
        create_phone_check = PhoneNumberCheck.objects.create(phone_number='09129487433', user_ip='127.0.0.1',
                                                             registration_status=True, wrong_password_count=2)
        UserAccount.objects.create(password=password, phone_register=create_phone_check)

    def test_login_success(self):
        url = reverse('api_urls:authorization:login-login')
        data = {'phone_number': '09129487433', 'password': '12345'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.json())

    def test_login_failed(self):
        url = reverse('api_urls:authorization:login-login')
        data = {'phone_number': '09129487433', 'password': '12'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_locked(self):
        url = reverse('api_urls:authorization:login-login')
        data = {'phone_number': '09129487433', 'password': '12'}
        first_try = self.client.post(url, data=data)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
