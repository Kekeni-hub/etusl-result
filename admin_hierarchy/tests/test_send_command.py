from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from unittest.mock import patch

class SendNotificationCommandTests(TestCase):

    @patch('Etu_student_result.firebase_service.init_firebase')
    @patch('Etu_student_result.firebase_service.messaging')
    def test_send_test_notification_missing_credentials(self, mock_messaging, mock_init):
        # Unset setting
        from django.conf import settings
        with self.settings(FIREBASE_CREDENTIALS=''):
            with self.assertRaises(CommandError):
                call_command('send_test_notification', 'fake-token')

    @patch('Etu_student_result.firebase_service.init_firebase')
    @patch('Etu_student_result.firebase_service.messaging')
    def test_send_test_notification_success(self, mock_messaging, mock_init):
        mock_messaging.send.return_value = 'ok'
        from django.conf import settings
        with self.settings(FIREBASE_CREDENTIALS='path'):
            # Should not raise
            call_command('send_test_notification', 'fake-token')
            mock_messaging.send.assert_called()
