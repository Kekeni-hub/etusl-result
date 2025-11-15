from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import Faculty, Department
from admin_hierarchy.models import HeadOfDepartment, DeanOfFaculty
import csv
from datetime import datetime


class Command(BaseCommand):
    help = 'Create superuser and admin staff with credentials'

    def handle(self, *args, **options):
        credentials = []

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@etusl.edu.sl',
                password='Admin@2025'
            )
            credentials.append({
                'Role': 'Superuser',
                'Username': 'admin',
                'Email': 'admin@etusl.edu.sl',
                'Password': 'Admin@2025',
                'Faculty': 'N/A',
                'Department': 'N/A'
            })
            self.stdout.write(self.style.SUCCESS('✓ Superuser created: admin'))

        # Get all faculties (work with existing ones)
        faculties = Faculty.objects.all()

        for faculty in faculties:
            # Create Dean for each faculty if doesn't exist
            if not hasattr(faculty, 'dean') or faculty.dean is None:
                fcode = faculty.code.upper()
                dean_username = f'dean_{fcode.lower()}'
                if not User.objects.filter(username=dean_username).exists():
                    dean_password = f'DeanPass@{fcode}2025'
                    dean_user = User.objects.create_user(
                        username=dean_username,
                        email=f'dean_{fcode.lower()}@etusl.edu.sl',
                        password=dean_password,
                        first_name='Dean',
                        last_name=faculty.code
                    )
                    DeanOfFaculty.objects.create(
                        user=dean_user,
                        dean_id=f'D{faculty.id:03d}',
                        faculty=faculty,
                        email=f'dean_{fcode.lower()}@etusl.edu.sl',
                        is_active=True
                    )
                    credentials.append({
                        'Role': 'Faculty Admin/Dean',
                        'Username': dean_username,
                        'Email': f'dean_{fcode.lower()}@etusl.edu.sl',
                        'Password': dean_password,
                        'Faculty': faculty.name,
                        'Department': 'All (Faculty-wide)'
                    })
                    self.stdout.write(self.style.SUCCESS(f'✓ Dean created for {faculty.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⊙ Dean already exists for {faculty.name}'))

        # Create department heads
        departments = Department.objects.all()
        for dept in departments:
            # Skip if HOD already exists for this department
            if not hasattr(dept, 'hod') or dept.hod is None:
                hod_username = f'hod_{dept.code.lower()}'
                if not User.objects.filter(username=hod_username).exists():
                    hod_password = f'HODPass@{dept.code}2025'
                    hod_user = User.objects.create_user(
                        username=hod_username,
                        email=f'hod_{dept.code.lower()}@etusl.edu.sl',
                        password=hod_password,
                        first_name='Head',
                        last_name='Department'
                    )
                    HeadOfDepartment.objects.create(
                        user=hod_user,
                        hod_id=f'H{dept.id:03d}',
                        department=dept,
                        email=f'hod_{dept.code.lower()}@etusl.edu.sl',
                        is_active=True
                    )
                    credentials.append({
                        'Role': 'Department Head',
                        'Username': hod_username,
                        'Email': f'hod_{dept.code.lower()}@etusl.edu.sl',
                        'Password': hod_password,
                        'Faculty': dept.faculty.name,
                        'Department': dept.name
                    })
                    self.stdout.write(self.style.SUCCESS(f'✓ HOD created for {dept.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⊙ HOD already exists for {dept.name}'))

        # Write credentials to CSV file
        csv_filename = f'admin_credentials_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Role', 'Username', 'Email', 'Password', 'Faculty', 'Department']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(credentials)

        self.stdout.write(self.style.SUCCESS(f'\n✓ All credentials saved to: {csv_filename}'))
        self.stdout.write(self.style.SUCCESS(f'Total accounts created: {len(credentials)}'))
