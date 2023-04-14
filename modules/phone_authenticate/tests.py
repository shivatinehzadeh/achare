from unittest.mock import patch
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from base.models import PhoneNumberCheck


class AuthenticateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_phone_check = PhoneNumberCheck.objects.create(phone_number='09129487433', user_ip='127.0.0.1',
                                                             registration_status=True)

    def test_phone_check_success(self):
        url = reverse('api_urls:phone-authenticate:get-phone')
        data = {'phone_number': '09059046144'}
        response = self.client.post(url, data=data)
        json_response = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(False, json_response['registration_status'])

    def test_phone_check_exists_success(self):
        url = reverse('api_urls:phone-authenticate:get-phone')
        data = {'phone_number': '09129487433'}
        response = self.client.post(url, data=data)
        json_response = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(True, json_response['registration_status'])


class OTPTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_phone_check = PhoneNumberCheck.objects.create(phone_number='09129487433', user_ip='127.0.0.1',
                                                             registration_status=False)

    @patch('base.otp_handler.OTPHandler.send_otp')
    def test_send_otp_success(self, mock_Response):
        mock_Response.return_value = '123456'
        url = reverse('api_urls:phone-authenticate:otp-send-otp-request')
        data = {'phone_number': '09129487433'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('base.otp_handler.OTPHandler.verify_otp')
    def test_verify_otp_success(self, mock_otp):
        url = reverse('api_urls:phone-authenticate:otp-verify-otp-request')
        data = {'phone_number': '09129487433', 'otp_string': '12345'}
        mock_otp.return_value = True
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('base.otp_handler.OTPHandler.verify_otp')
    def test_verify_otp_failed(self, mock_otp):
        create_phone_check = PhoneNumberCheck.objects.create(phone_number='09059046144', user_ip='127.0.0.1',
                                                             registration_status=True, user_ip_wrong_count=2)
        url = reverse('api_urls:phone-authenticate:otp-verify-otp-request')
        data = {'phone_number': '09059046144', 'otp_string': '12345'}
        mock_otp.return_value = True
        response = self.client.post(url, data=data)
        # registered
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('base.otp_handler.OTPHandler.verify_otp')
    def test_verify_otp_locked(self, mock_otp):
        create_phone_check = PhoneNumberCheck.objects.create(phone_number='09059046144', user_ip='127.0.0.1',
                                                             registration_status=False, user_ip_wrong_count=2)
        url = reverse('api_urls:phone-authenticate:otp-verify-otp-request')
        data = {'phone_number': '09059046144', 'otp_string': '12345'}
        mock_otp.return_value = False
        response = self.client.post(url, data=data)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
