#!/usr/bin/env python
import os
import sys
import django
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
from django.contrib.auth.models import User
from lecturer.models import Lecturer
from student.models import Student, Program, Department, Faculty
from admin_hierarchy.models import HeadOfDepartment

# Create client
client = Client()

# Get or create test data
faculty = Faculty.objects.first() or Faculty.objects.create(name='Test Faculty')
department = Department.objects.first() or Department.objects.create(name='Test Department', faculty=faculty)
program = Program.objects.first() or Program.objects.create(name='Test Program', department=department)

# Create or get test lecturer
lecturer_user = User.objects.filter(username='testlecturer123').first()
if not lecturer_user:
    lecturer_user = User.objects.create_user(
        username='testlecturer123',
        email='testlecturer@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Lecturer'
    )

lecturer = Lecturer.objects.filter(user=lecturer_user).first()
if not lecturer:
    lecturer = Lecturer.objects.create(
        user=lecturer_user,
        lecturer_id='LEC001',
        email='testlecturer@example.com',
        faculty=faculty,
        department=department,
        is_verified=True
    )

# Create test students
students_data = [
    ('STU001', 'John', 'Doe'),
    ('STU002', 'Jane', 'Smith'),
    ('STU003', 'Bob', 'Johnson'),
]

students = []
for student_id, first_name, last_name in students_data:
    existing_student = Student.objects.filter(student_id=student_id).first()
    if existing_student:
        students.append(existing_student)
        continue
    
    user = User.objects.create_user(
        username=f'student_{student_id}',
        email=f'{student_id}@example.com',
        password='testpass123',
        first_name=first_name,
        last_name=last_name
    )
    
    student = Student.objects.create(
        user=user,
        student_id=student_id,
        phone='1234567890',
        program=program,
        department=department,
        faculty=faculty,
    )
    students.append(student)

# Create HOD for approval
hod_user = User.objects.filter(username='testhod123').first()
if not hod_user:
    hod_user = User.objects.create_user(
        username='testhod123',
        email='testhod@example.com',
        password='testpass123',
        first_name='Head',
        last_name='Department'
    )

hod = HeadOfDepartment.objects.filter(user=hod_user).first()
if not hod:
    hod = HeadOfDepartment.objects.create(
        user=hod_user,
        faculty=faculty,
        department=department,
        is_active=True
    )

print("=" * 60)
print("Testing CSV Upload Feature")
print("=" * 60)

# Test 1: Access CSV upload page (GET)
print("\n[TEST 1] GET /lecturer/upload-results-csv/ (unauthenticated)")
response = client.get('/lecturer/upload-results-csv/')
print(f"Status: {response.status_code} (expected 302 redirect to login)")

# Login as lecturer
print("\n[Logging in as lecturer...]")
login_success = client.login(username='testlecturer123', password='testpass123')
print(f"Login successful: {login_success}")

# Test 2: Access CSV upload page (GET, authenticated)
print("\n[TEST 2] GET /lecturer/upload-results-csv/ (authenticated)")
response = client.get('/lecturer/upload-results-csv/')
print(f"Status: {response.status_code} (expected 200)")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
print("✓ Form page loaded successfully")

# Test 3: Download CSV template
print("\n[TEST 3] GET /lecturer/download-csv-template/")
response = client.get('/lecturer/download-csv-template/')
print(f"Status: {response.status_code} (expected 200)")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
print("✓ CSV template downloaded successfully")
print(f"Content-Type: {response['Content-Type']}")

# Test 4: Upload valid CSV
print("\n[TEST 4] POST /lecturer/upload-results-csv/ (valid CSV)")

# Create valid CSV content
csv_content = """Student_ID,Module_Code,Score,Total_Score
STU001,CS101,85,100
STU002,CS101,92,100
STU003,CS102,78,100
"""

csv_file = BytesIO(csv_content.encode())
csv_file.name = 'valid_results.csv'

response = client.post('/lecturer/upload-results-csv/', {
    'csv_file': csv_file,
    'program': program.id,
    'academic_year': '2024/2025',
    'semester': '1',
})

print(f"Status: {response.status_code}")
if response.status_code == 302:
    print("✓ Form submitted successfully, redirected to dashboard")
else:
    print(f"✗ Unexpected status code: {response.status_code}")
    if hasattr(response, 'content'):
        print(f"  Response: {response.content[:200]}")

# Test 5: Upload CSV with missing required field
print("\n[TEST 5] POST /lecturer/upload-results-csv/ (missing Student_ID)")

csv_content_bad = """Module_Code,Score,Total_Score
CS101,85,100
CS101,92,100
"""

csv_file = BytesIO(csv_content_bad.encode())
csv_file.name = 'bad_results.csv'

response = client.post('/lecturer/upload-results-csv/', {
    'csv_file': csv_file,
    'program': program.id,
    'academic_year': '2024/2025',
    'semester': '1',
})

print(f"Status: {response.status_code}")
if response.status_code == 302:
    print("✓ Invalid CSV was rejected and redirected")
else:
    print(f"Response: {response.status_code}")

# Test 6: Upload CSV without file
print("\n[TEST 6] POST /lecturer/upload-results-csv/ (no file)")

response = client.post('/lecturer/upload-results-csv/', {
    'program': program.id,
    'academic_year': '2024/2025',
    'semester': '1',
})

print(f"Status: {response.status_code}")
if response.status_code == 302:
    print("✓ Empty submission was rejected and redirected")
else:
    print(f"Response: {response.status_code}")

print("\n" + "=" * 60)
print("All CSV upload tests completed!")
print("=" * 60)
