import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient

USERNAME = 'api_test_user'
PASSWORD = 'ApiTestPass123!'

# Create or reset the test user
user, created = User.objects.get_or_create(username=USERNAME, defaults={'email': 'api_test@example.com', 'first_name': 'API', 'last_name': 'Test'})
user.set_password(PASSWORD)
user.is_active = True
user.save()
print('User created/reset:', USERNAME)

client = APIClient()

# Try form-encoded POST
resp = client.post('/api-token-auth/', {'username': USERNAME, 'password': PASSWORD}, format='multipart')
print('Form-encoded POST status:', resp.status_code, 'data:', resp.data)

# Try JSON POST
resp_json = client.post('/api-token-auth/', {'username': USERNAME, 'password': PASSWORD}, format='json')
print('JSON POST status:', resp_json.status_code, 'data:', resp_json.data)

# If token returned, print instructions
if resp_json.status_code == 200 and 'token' in resp_json.data:
    token = resp_json.data['token']
    print('\nSuccess! Use this token in PowerShell:')
    print("$token = '" + token + "'")
    print("Invoke-RestMethod -Uri 'http://localhost:8000/api/students/' -Method Get -Headers @{ Authorization = \"Token $token\" }")
else:
    print('\nToken auth did not succeed via APIClient; check configuration.')
