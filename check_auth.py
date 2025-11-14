#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
sys.path.insert(0, 'c:\\Etu_student_result')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

print("=" * 60)
print("LOGIN CREDENTIAL DIAGNOSTIC REPORT")
print("=" * 60)

# 1. Check all users
print("\n1. ALL USERS IN DATABASE:")
print("-" * 60)
all_users = User.objects.all()
print(f"Total users: {all_users.count()}\n")
for user in all_users:
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Active: {user.is_active}")
    print(f"  Staff: {user.is_staff}")
    print(f"  Superuser: {user.is_superuser}")
    print()

# 2. Check superusers specifically
print("2. SUPERUSERS:")
print("-" * 60)
superusers = User.objects.filter(is_superuser=True)
for su in superusers:
    print(f"  {su.username} ({su.email})")

# 3. Test authentication
print("\n3. TESTING AUTHENTICATION:")
print("-" * 60)
test_creds = [
    ('admin_main', 'Admin@2025'),
    ('admin', 'admin123'),
    ('hod_admin', 'HOD@2025'),
    ('dean_admin', 'DEAN@2025'),
]

for username, password in test_creds:
    user = authenticate(username=username, password=password)
    if user:
        print(f"  ✓ {username} / {password} - WORKS")
    else:
        print(f"  ✗ {username} / {password} - FAILED")
        # Check if user exists
        try:
            u = User.objects.get(username=username)
            print(f"    (User exists but password incorrect or user inactive)")
        except User.DoesNotExist:
            print(f"    (User does not exist)")

print("\n" + "=" * 60)
print("END OF REPORT")
print("=" * 60)
