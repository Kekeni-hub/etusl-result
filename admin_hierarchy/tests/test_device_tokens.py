from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse
from unittest import mock

User = get_user_model()


class DeviceTokenAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_register_device_token(self):
        url = reverse('api_device_tokens')
        payload = {'token': 'fake_fcm_token_12345', 'platform': 'android', 'metadata': {'app_version': '1.0'}}
        resp = self.client.post(url, payload, format='json')
        self.assertIn(resp.status_code, (200, 201))
        self.assertEqual(resp.data['token'], payload['token'])

    def test_unregister_device_token(self):
        url = reverse('api_device_tokens')
        payload = {'token': 'fake_fcm_token_to_delete'}
        # register
        self.client.post(url, payload, format='json')
        # delete
        resp = self.client.delete(url, payload, format='json')
        self.assertEqual(resp.status_code, 200)


class FirebaseVerifyIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @mock.patch('Etu_student_result.firebase_service.verify_id_token')
    def test_verify_creates_user_and_returns_token(self, mock_verify):
        mock_verify.return_value = {'uid': 'firebase-uid-1', 'email': 'user@example.com', 'name': 'Test User'}
        url = reverse('firebase_verify_token')
        resp = self.client.post(url, {'id_token': 'fake'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['email'], 'user@example.com')
*** End Patch