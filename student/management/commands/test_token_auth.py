from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class Command(BaseCommand):
    help = 'Create test user and attempt to obtain token via /api-token-auth/'

    def handle(self, *args, **options):
        USERNAME = 'api_test_user'
        PASSWORD = 'ApiTestPass123!'

        user, created = User.objects.get_or_create(username=USERNAME, defaults={'email': 'api_test@example.com', 'first_name': 'API', 'last_name': 'Test'})
        user.set_password(PASSWORD)
        user.is_active = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f'User created/reset: {USERNAME}'))

        client = APIClient()
        # form-encoded
        resp = client.post('/api-token-auth/', {'username': USERNAME, 'password': PASSWORD}, format='multipart')
        self.stdout.write(f'Form POST status: {resp.status_code} data: {resp.data}')
        # json
        resp_json = client.post('/api-token-auth/', {'username': USERNAME, 'password': PASSWORD}, format='json')
        self.stdout.write(f'JSON POST status: {resp_json.status_code} data: {resp_json.data}')

        if resp_json.status_code == 200 and 'token' in resp_json.data:
            token = resp_json.data['token']
            self.stdout.write(self.style.SUCCESS('\nSuccess! Token: ' + token))
            self.stdout.write('\nPowerShell example:')
            self.stdout.write(f"$token = '{token}'")
            self.stdout.write("Invoke-RestMethod -Uri 'http://localhost:8000/api/students/' -Method Get -Headers @{ Authorization = \"Token $token\" }")
        else:
            self.stdout.write(self.style.ERROR('\nToken auth did not succeed via APIClient; check configuration.'))
