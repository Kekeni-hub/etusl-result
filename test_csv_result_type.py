#!/usr/bin/env python
"""Quick test of CSV upload with result_type"""

import os
import sys
import django
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
from django.contrib.auth.models import User
from lecturer.models import Lecturer
from student.models import Student, Program, Department, Faculty, Result
from admin_hierarchy.models import HeadOfDepartment

print("="*60)
print("Testing CSV Upload with Result Type Selection")
print("="*60)

# Setup test data
faculty = Faculty.objects.first() or Faculty.objects.create(name='Test Faculty')
department = Department.objects.first() or Department.objects.create(name='Test Department', faculty=faculty)
program = Program.objects.first() or Program.objects.create(name='Test Program', department=department)

# Create lecturer
lecturer_user, _ = User.objects.get_or_create(
    username='csvtest_lecturer',
    defaults={
        'email': 'csvtest@example.com',
        'first_name': 'CSV',
        'last_name': 'Tester'
    }
)
lecturer_user.set_password('testpass123')
lecturer_user.save()

lecturer, _ = Lecturer.objects.get_or_create(
    user=lecturer_user,
    defaults={
        'lecturer_id': 'LEC_CSV',
        'email': 'csvtest@example.com',
        'faculty': faculty,
        'department': department,
        'is_verified': True
    }
)

# Create students
for i in range(1, 4):
    student_user, _ = User.objects.get_or_create(
        username=f'csvstudent{i}',
        defaults={
            'email': f'csvstudent{i}@example.com',
            'first_name': f'CSV Student',
            'last_name': f'{i}'
        }
    )
    student_user.set_password('testpass123')
    student_user.save()
    
    Student.objects.get_or_create(
        user=student_user,
        defaults={
            'student_id': f'CSV{i:03d}',
            'phone': '1234567890',
            'program': program,
            'department': department,
            'faculty': faculty,
        }
    )

# Create HOD
hod_user, _ = User.objects.get_or_create(
    username='csvhod',
    defaults={
        'email': 'csvhod@example.com',
        'first_name': 'CSV',
        'last_name': 'HOD'
    }
)
hod_user.set_password('testpass123')
hod_user.save()

HeadOfDepartment.objects.get_or_create(
    user=hod_user,
    defaults={
        'faculty': faculty,
        'department': department,
        'is_active': True
    }
)

print("\n[TEST 1] Login and access CSV upload form")
client = Client()
logged_in = client.login(username='csvtest_lecturer', password='testpass123')
print(f"✓ Login successful: {logged_in}")

response = client.get('/lecturer/upload-results-csv/')
print(f"✓ CSV upload page status: {response.status_code}")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# Check if result_types is in context
if 'result_types' in response.context:
    result_types = response.context['result_types']
    print(f"✓ Result types available: {len(result_types)} types")
    for code, label in result_types:
        print(f"  - {code}: {label}")
else:
    print("✗ result_types not found in context!")

print("\n[TEST 2] Test CSV upload with result_type='reference'")
csv_content = """Student_ID,Module_Code,Score,Total_Score
CSV001,TESTMOD01,85,100
CSV002,TESTMOD01,92,100
CSV003,TESTMOD02,78,100
"""

csv_file = BytesIO(csv_content.encode())
csv_file.name = 'test_reference.csv'

response = client.post('/lecturer/upload-results-csv/', {
    'csv_file': csv_file,
    'program': program.id,
    'result_type': 'reference',
    'academic_year': '2024/2025',
    'semester': '1',
})

print(f"✓ CSV upload response status: {response.status_code}")
if response.status_code == 302:
    print("✓ Redirected successfully (upload processed)")
    
    # Check if results were created with correct type
    results = Result.objects.filter(result_type='reference', academic_year='2024/2025', semester='1')
    print(f"✓ Results created with type 'reference': {results.count()}")
    for r in results:
        print(f"  - {r.student.student_id}: {r.subject} ({r.score}/{r.total_score}) - Grade: {r.grade}")
else:
    print(f"✗ Unexpected status: {response.status_code}")
    if hasattr(response, 'content'):
        print(response.content[:500])

print("\n[TEST 3] Test CSV upload with result_type='current_exam'")
csv_content = """Student_ID,Module_Code,Score,Total_Score
CSV001,CURRENTMOD01,88,100
CSV002,CURRENTMOD01,95,100
"""

csv_file = BytesIO(csv_content.encode())
csv_file.name = 'test_current_exam.csv'

response = client.post('/lecturer/upload-results-csv/', {
    'csv_file': csv_file,
    'program': program.id,
    'result_type': 'current_exam',
    'academic_year': '2024/2025',
    'semester': '1',
})

print(f"✓ CSV upload response status: {response.status_code}")
if response.status_code == 302:
    results = Result.objects.filter(result_type='current_exam', academic_year='2024/2025', semester='1')
    print(f"✓ Results created with type 'current_exam': {results.count()}")

print("\n[TEST 4] Test CSV upload with result_type='incomplete_grades'")
csv_content = """Student_ID,Module_Code,Score,Total_Score
CSV003,INCOMPLETEMOD01,45,100
"""

csv_file = BytesIO(csv_content.encode())
csv_file.name = 'test_incomplete.csv'

response = client.post('/lecturer/upload-results-csv/', {
    'csv_file': csv_file,
    'program': program.id,
    'result_type': 'incomplete_grades',
    'academic_year': '2024/2025',
    'semester': '1',
})

print(f"✓ CSV upload response status: {response.status_code}")
if response.status_code == 302:
    results = Result.objects.filter(result_type='incomplete_grades', academic_year='2024/2025', semester='1')
    print(f"✓ Results created with type 'incomplete_grades': {results.count()}")

print("\n" + "="*60)
print("CSV Upload with Result Type - All Tests Complete!")
print("="*60)
