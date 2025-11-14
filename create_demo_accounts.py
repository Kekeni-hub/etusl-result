#!/usr/bin/env python
"""
Script to create demo HOD and DEAN accounts for testing the multi-tier approval system.
Run with: python manage.py shell < create_demo_accounts.py
"""

from django.contrib.auth.models import User
from admin_hierarchy.models import HeadOfDepartment, DeanOfFaculty
from student.models import Department, Faculty

# Create HOD accounts
print("=" * 60)
print("Creating Demo HOD Accounts")
print("=" * 60)

# Get or create faculties first
faculty_sci, _ = Faculty.objects.get_or_create(
    name="Faculty of Science",
    defaults={"code": "FAC-SCI", "description": "Faculty of Science and Technology"}
)
faculty_eng, _ = Faculty.objects.get_or_create(
    name="Faculty of Engineering",
    defaults={"code": "FAC-ENG", "description": "Faculty of Engineering and Architecture"}
)

# Get or create departments
dept_cs, _ = Department.objects.get_or_create(
    name="Computer Science",
    defaults={"code": "DEPT-CS", "faculty": faculty_sci, "description": "Department of Computer Science"}
)
dept_eng, _ = Department.objects.get_or_create(
    name="Engineering",
    defaults={"code": "DEPT-ENG", "faculty": faculty_eng, "description": "Department of Engineering"}
)

# Create HOD for Computer Science
hod_cs_user, created = User.objects.get_or_create(
    username="hod_cs",
    defaults={
        "email": "hod.cs@etu.local",
        "first_name": "Dr.",
        "last_name": "Mensah"
    }
)
if created:
    hod_cs_user.set_password("HodCS@123")
    hod_cs_user.save()
    print(f"✓ Created user: {hod_cs_user.username}")

hod_cs, created = HeadOfDepartment.objects.get_or_create(
    user=hod_cs_user,
    defaults={
        "hod_id": "HOD/CS/001",
        "email": "hod.cs@etu.local",
        "phone": "+233501234567",
        "department": dept_cs,
        "office_location": "CS Building, Room 201",
        "is_active": True
    }
)
if created:
    print(f"✓ Created HOD profile: {hod_cs.hod_id} ({dept_cs.name})")
    print(f"  Email: {hod_cs.email}")
    print(f"  Password: HodCS@123")

# Create HOD for Engineering
hod_eng_user, created = User.objects.get_or_create(
    username="hod_eng",
    defaults={
        "email": "hod.eng@etu.local",
        "first_name": "Prof.",
        "last_name": "Osei"
    }
)
if created:
    hod_eng_user.set_password("HodEng@123")
    hod_eng_user.save()
    print(f"✓ Created user: {hod_eng_user.username}")

hod_eng, created = HeadOfDepartment.objects.get_or_create(
    user=hod_eng_user,
    defaults={
        "hod_id": "HOD/ENG/001",
        "email": "hod.eng@etu.local",
        "phone": "+233502234567",
        "department": dept_eng,
        "office_location": "Engineering Building, Room 301",
        "is_active": True
    }
)
if created:
    print(f"✓ Created HOD profile: {hod_eng.hod_id} ({dept_eng.name})")
    print(f"  Email: {hod_eng.email}")
    print(f"  Password: HodEng@123")

# Create DEAN accounts
print("\n" + "=" * 60)
print("Creating Demo DEAN Accounts")
print("=" * 60)

# Create DEAN for Faculty of Science
dean_sci_user, created = User.objects.get_or_create(
    username="dean_science",
    defaults={
        "email": "dean.science@etu.local",
        "first_name": "Prof.",
        "last_name": "Adjei"
    }
)
if created:
    dean_sci_user.set_password("DeanSci@123")
    dean_sci_user.save()
    print(f"✓ Created user: {dean_sci_user.username}")

dean_sci, created = DeanOfFaculty.objects.get_or_create(
    user=dean_sci_user,
    defaults={
        "dean_id": "DEAN/SCI/001",
        "email": "dean.science@etu.local",
        "phone": "+233503234567",
        "faculty": faculty_sci,
        "office_location": "Science Building, Room 401",
        "is_active": True
    }
)
if created:
    print(f"✓ Created DEAN profile: {dean_sci.dean_id} ({faculty_sci.name})")
    print(f"  Email: {dean_sci.email}")
    print(f"  Password: DeanSci@123")

# Create DEAN for Faculty of Engineering
dean_eng_user, created = User.objects.get_or_create(
    username="dean_engineering",
    defaults={
        "email": "dean.engineering@etu.local",
        "first_name": "Dr.",
        "last_name": "Anane"
    }
)
if created:
    dean_eng_user.set_password("DeanEng@123")
    dean_eng_user.save()
    print(f"✓ Created user: {dean_eng_user.username}")

dean_eng, created = DeanOfFaculty.objects.get_or_create(
    user=dean_eng_user,
    defaults={
        "dean_id": "DEAN/ENG/001",
        "email": "dean.engineering@etu.local",
        "phone": "+233504234567",
        "faculty": faculty_eng,
        "office_location": "Engineering Building, Room 402",
        "is_active": True
    }
)
if created:
    print(f"✓ Created DEAN profile: {dean_eng.dean_id} ({faculty_eng.name})")
    print(f"  Email: {dean_eng.email}")
    print(f"  Password: DeanEng@123")

print("\n" + "=" * 60)
print("DEMO ACCOUNT SUMMARY")
print("=" * 60)
print("\n📋 HEAD OF DEPARTMENT (HOD) ACCOUNTS:")
print("  1. Computer Science HOD:")
print("     Email: hod.cs@etu.local")
print("     Password: HodCS@123")
print("     Department: Computer Science")
print("\n  2. Engineering HOD:")
print("     Email: hod.eng@etu.local")
print("     Password: HodEng@123")
print("     Department: Engineering")

print("\n📋 DEAN OF FACULTY (DEAN) ACCOUNTS:")
print("  1. Faculty of Science DEAN:")
print("     Email: dean.science@etu.local")
print("     Password: DeanSci@123")
print("     Faculty: Faculty of Science")
print("\n  2. Faculty of Engineering DEAN:")
print("     Email: dean.engineering@etu.local")
print("     Password: DeanEng@123")
print("     Faculty: Faculty of Engineering")

print("\n🔗 Access URLs:")
print("  HOD Login: http://127.0.0.1:8000/admin-hierarchy/hod/login/")
print("  DEAN Login: http://127.0.0.1:8000/admin-hierarchy/dean/login/")

print("\n" + "=" * 60)
