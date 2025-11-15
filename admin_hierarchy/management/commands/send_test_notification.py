from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from Etu_student_result.firebase_service import send_fcm_message, init_firebase


class Command(BaseCommand):
    help = 'Send a test Firebase Cloud Messaging notification to a device token.'

    def add_arguments(self, parser):
        parser.add_argument('token', type=str, help='FCM device registration token')
        parser.add_argument('--title', type=str, default='ETU Test', help='Notification title')
        parser.add_argument('--body', type=str, default='This is a test notification from ETU.', help='Notification body')

    def handle(self, *args, **options):
        token = options['token']
        title = options['title']
        body = options['body']

        if not settings.FIREBASE_CREDENTIALS:
            raise CommandError('FIREBASE_CREDENTIALS is not set in settings or environment.')

        try:
            init_firebase(settings.FIREBASE_CREDENTIALS)
        except Exception as e:
            raise CommandError(f'Failed to initialize Firebase: {e}')

        try:
            response = send_fcm_message(token, title, body)
            self.stdout.write(self.style.SUCCESS(f'Message sent: {response}'))
        except Exception as e:
            raise CommandError(f'Failed to send message: {e}')
