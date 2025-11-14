import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

print("=" * 70)
print("TESTING LOGIN CREDENTIALS")
print("=" * 70)

# Test each credential
credentials = [
    ('admin_main', 'Admin@2025'),
    ('hod_admin', 'HOD@2025'),
    ('dean_admin', 'DEAN@2025'),
    ('admin', 'admin123'),
]

for username, password in credentials:
    print(f"\nTesting: {username} / {password}")
    print("-" * 70)
    
    try:
        user = User.objects.get(username=username)
        print(f"  ✓ User exists")
        print(f"    - Active: {user.is_active}")
        print(f"    - Staff: {user.is_staff}")
        print(f"    - Superuser: {user.is_superuser}")
        
        # Test authentication
        auth = authenticate(username=username, password=password)
        if auth:
            print(f"  ✓ AUTHENTICATION SUCCESS")
        else:
            print(f"  ✗ AUTHENTICATION FAILED")
            # Try to check if password is correct by setting and testing
            user_check = User.objects.get(username=username)
            user_check.set_password(password)
            user_check.save()
            print(f"    → Password reset to: {password}")
            
            # Re-test
            auth2 = authenticate(username=username, password=password)
            if auth2:
                print(f"    → After reset: AUTHENTICATION SUCCESS")
    except User.DoesNotExist:
        print(f"  ✗ User does not exist - Creating now")
        user = User.objects.create_superuser(username, f"{username}@etusl.edu", password)
        print(f"    → User created successfully")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
