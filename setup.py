# Setup script to initialize the database and create an admin user
# Run this from Django shell: python manage.py shell < setup.py

from django.contrib.auth.models import User
from exam_officer.models import ExamOfficer
from student.models import Faculty, Department, Program

# Create default admin user if it doesn't exist
if not User.objects.filter(username='admin@university.edu').exists():
    admin_user = User.objects.create_superuser(
        username='admin@university.edu',
        email='admin@university.edu',
        password='admin123',
        first_name='Admin',
        last_name='Officer'
    )
    
    # Create ExamOfficer profile
    ExamOfficer.objects.create(
        user=admin_user,
        officer_id='ADM001',
        email='admin@university.edu',
        phone='+1234567890',
        office_location='Admin Building - Room 101',
        is_active=True
    )
    print("✓ Admin user created successfully!")
    print("  Username: admin@university.edu")
    print("  Password: admin123")
else:
    print("✗ Admin user already exists")

# Create sample faculties
faculties_data = [
    {'name': 'Faculty of Science', 'code': 'FOS'},
    {'name': 'Faculty of Engineering', 'code': 'FOE'},
    {'name': 'Faculty of Arts', 'code': 'FOA'},
    {'name': 'Faculty of Medicine', 'code': 'FOM'},
    {'name': 'Faculty of Business', 'code': 'FOB'},
]

for fac_data in faculties_data:
    faculty, created = Faculty.objects.get_or_create(
        code=fac_data['code'],
        defaults={'name': fac_data['name']}
    )
    if created:
        print(f"✓ Created faculty: {faculty.name}")
    else:
        print(f"✗ Faculty already exists: {faculty.name}")

# Create sample departments
departments_data = [
    {'name': 'Computer Science', 'code': 'CS', 'faculty_code': 'FOS'},
    {'name': 'Physics', 'code': 'PHY', 'faculty_code': 'FOS'},
    {'name': 'Chemistry', 'code': 'CHM', 'faculty_code': 'FOS'},
    {'name': 'Civil Engineering', 'code': 'CE', 'faculty_code': 'FOE'},
    {'name': 'Mechanical Engineering', 'code': 'ME', 'faculty_code': 'FOE'},
    {'name': 'English', 'code': 'ENG', 'faculty_code': 'FOA'},
    {'name': 'History', 'code': 'HIS', 'faculty_code': 'FOA'},
]

for dept_data in departments_data:
    try:
        faculty = Faculty.objects.get(code=dept_data['faculty_code'])
        department, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults={'name': dept_data['name'], 'faculty': faculty}
        )
        if created:
            print(f"✓ Created department: {department.name}")
        else:
            print(f"✗ Department already exists: {department.name}")
    except Faculty.DoesNotExist:
        print(f"✗ Faculty not found: {dept_data['faculty_code']}")

# Create sample programs
programs_data = [
    {'name': 'BSc Computer Science', 'code': 'BSCCS', 'dept_code': 'CS'},
    {'name': 'BSc Physics', 'code': 'BSCPHY', 'dept_code': 'PHY'},
    {'name': 'BTech Civil Engineering', 'code': 'BTCE', 'dept_code': 'CE'},
    {'name': 'BA English', 'code': 'BAENG', 'dept_code': 'ENG'},
]

for prog_data in programs_data:
    try:
        department = Department.objects.get(code=prog_data['dept_code'])
        program, created = Program.objects.get_or_create(
            code=prog_data['code'],
            defaults={'name': prog_data['name'], 'department': department}
        )
        if created:
            print(f"✓ Created program: {program.name}")
        else:
            print(f"✗ Program already exists: {program.name}")
    except Department.DoesNotExist:
        print(f"✗ Department not found: {prog_data['dept_code']}")

print("\n✓ Database setup completed!")
