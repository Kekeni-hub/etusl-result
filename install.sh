#!/bin/bash
# Installation script for Student Result Management System

echo "================================================"
echo "Student Result Management System - Setup Script"
echo "================================================"

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python --version)"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # For Linux/Mac
# For Windows, use: venv\Scripts\activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create initial data
echo ""
echo "Creating initial data (faculties, departments, programs, admin user)..."
python manage.py shell << EOF
from django.contrib.auth.models import User
from admin.models import ExamOfficer
from student.models import Faculty, Department, Program

# Create default admin user
if not User.objects.filter(username='admin@university.edu').exists():
    admin_user = User.objects.create_superuser(
        username='admin@university.edu',
        email='admin@university.edu',
        password='admin123',
        first_name='Admin',
        last_name='Officer'
    )
    ExamOfficer.objects.create(
        user=admin_user,
        officer_id='ADM001',
        email='admin@university.edu',
        is_active=True
    )
    print("✓ Admin user created!")

# Create faculties
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

print("\n✓ Database setup completed!")
EOF

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "To start the development server, run:"
echo "  python manage.py runserver"
echo ""
echo "Then visit: http://127.0.0.1:8000"
echo ""
echo "Admin Login:"
echo "  URL: http://127.0.0.1:8000/officer/login/"
echo "  Email: admin@university.edu"
echo "  Password: admin123"
echo ""
echo "Django Admin:"
echo "  URL: http://127.0.0.1:8000/admin/"
echo "  Email: admin@university.edu"
echo "  Password: admin123"
echo ""
