#!/usr/bin/env python
"""Test the NEW dean_register_student endpoint."""
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
sys.path.insert(0, str(Path(__file__).parent))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from admin_hierarchy.models import DeanOfFaculty
from student.models import Faculty, Department, Program, Student

def test_new_endpoint():
    """Test the new simplified endpoint."""
    print("=" * 80)
    print("TESTING NEW DEAN_REGISTER_STUDENT ENDPOINT")
    print("=" * 80)
    
    client = Client(SERVER_NAME='127.0.0.1')
    
    # Get a real dean
    dean_user = User.objects.get(username='dean_spgs')
    client.force_login(dean_user)
    dean_profile = dean_user.dean_profile
    faculty = dean_profile.faculty
    
    print(f"\n[*] Dean: {dean_user.username}")
    print(f"[*] Faculty: {faculty.name}")
    
    # Test 1: GET the registration form
    print("\n[TEST 1] GET /dean/register-student/")
    response = client.get('/dean/register-student/')
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  [OK] Form page loaded")
    else:
        print(f"  [ERROR] Expected 200, got {response.status_code}")
        return
    
    # Get or create department and program
    department = Department.objects.filter(faculty=faculty).first()
    if not department:
        department = Department.objects.create(
            name='Test Department',
            code='TD',
            faculty=faculty
        )
    
    program = Program.objects.filter(department=department).first()
    if not program:
        program = Program.objects.create(
            name='Test Program',
            code='TP',
            department=department
        )
    
    print(f"\n[*] Using Department: {department.name}")
    print(f"[*] Using Program: {program.name}")
    
    # Test 2: POST with valid data
    print("\n[TEST 2] POST valid student registration")
    form_data = {
        'first_name': 'NewTest',
        'last_name': 'Student',
        'email': f'newtest_{os.urandom(3).hex()}@test.edu',
        'student_id': f'NTS{os.urandom(3).hex().upper()}',
        'phone': '+234-8012345678',
        'department': str(department.id),
        'program': str(program.id),
        'current_year': '1',
    }
    
    response = client.post('/dean/register-student/', data=form_data, follow=False)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 302:
        print(f"  [OK] Redirected to: {response.get('Location')}")
        # Check if student was created
        try:
            student = Student.objects.get(student_id=form_data['student_id'])
            print(f"  [OK] Student created: {student}")
        except Student.DoesNotExist:
            print(f"  [ERROR] Student not created!")
    elif response.status_code == 200:
        print(f"  [OK] Returned 200 (form with validation)")
        content = response.content.decode('utf-8', errors='ignore')
        if 'error' in content.lower() or 'invalid' in content.lower():
            print(f"  [INFO] Response contains validation feedback")
    else:
        print(f"  [ERROR] Unexpected status {response.status_code}")
        print(f"  Content: {response.content[:500].decode('utf-8', errors='ignore')}")
    
    # Test 3: POST with duplicate email (should show error, not 500)
    print("\n[TEST 3] POST with duplicate email (validation test)")
    dup_email = form_data['email']
    dup_form_data = {
        'first_name': 'Duplicate',
        'last_name': 'Email',
        'email': dup_email,
        'student_id': f'DUP{os.urandom(3).hex().upper()}',
        'phone': '+234-8012345678',
        'department': str(department.id),
        'program': str(program.id),
        'current_year': '1',
    }
    
    response = client.post('/dean/register-student/', data=dup_form_data, follow=False)
    print(f"  Status: {response.status_code}")
    
    if response.status_code >= 500:
        print(f"  [ERROR] Got 500 error! Form validation failed!")
    elif response.status_code == 200:
        print(f"  [OK] Returned 200 (showing form with error message)")
        content = response.content.decode('utf-8', errors='ignore')
        if 'already' in content.lower():
            print(f"  [OK] Error message displayed")
    else:
        print(f"  [STATUS] Got {response.status_code}")
    
    # Test 4: POST with duplicate student_id (should show error)
    print("\n[TEST 4] POST with duplicate student_id (validation test)")
    dup_student_id = form_data['student_id']
    dup_form_data['student_id'] = dup_student_id
    dup_form_data['email'] = f'dup2_{os.urandom(3).hex()}@test.edu'
    
    response = client.post('/dean/register-student/', data=dup_form_data, follow=False)
    print(f"  Status: {response.status_code}")
    
    if response.status_code >= 500:
        print(f"  [ERROR] Got 500 error!")
    elif response.status_code == 200:
        print(f"  [OK] Returned 200 (showing form with error)")
        content = response.content.decode('utf-8', errors='ignore')
        if 'already' in content.lower():
            print(f"  [OK] Error message displayed")
    else:
        print(f"  [STATUS] Got {response.status_code}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    test_new_endpoint()
