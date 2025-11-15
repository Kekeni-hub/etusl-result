import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

users = User.objects.filter(is_active=True)
print('Found', users.count(), 'active users')
for u in users:
    t, created = Token.objects.get_or_create(user=u)
    print(u.username, t.key)
