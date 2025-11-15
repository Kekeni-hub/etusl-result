import unittest
from unittest.mock import patch, MagicMock

from Etu_student_result import firebase_service


class FirebaseServiceTests(unittest.TestCase):

    @patch('Etu_student_result.firebase_service.firebase_admin')
    def test_init_firebase_raises_if_no_cred(self, mock_firebase_admin):
        # Ensure environment not set
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(RuntimeError):
                firebase_service.init_firebase(None)

    @patch('Etu_student_result.firebase_service.messaging')
    @patch('Etu_student_result.firebase_service.firebase_admin')
    def test_send_fcm_message_calls_messaging(self, mock_firebase_admin, mock_messaging):
        mock_messaging.send.return_value = 'msgid123'
        # Provide a fake init to avoid reading real creds
        with patch('Etu_student_result.firebase_service.init_firebase'):
            resp = firebase_service.send_fcm_message('token', 't', 'b', data={'k': 'v'})
            self.assertEqual(resp, 'msgid123')
            mock_messaging.send.assert_called()


if __name__ == '__main__':
    unittest.main()
