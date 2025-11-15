from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from student.models import Faculty, Department, Program, Student, Result, StudentSemesterFolder
from lecturer.models import Lecturer


class ExportArchiveTests(TestCase):
    def setUp(self):
        # create superuser and login
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'pass')
        self.client = Client()
        self.client.login(username='admin', password='pass')

        # create faculty/department/program
        self.fac = Faculty.objects.create(name='Science', code='SCI')
        self.dept = Department.objects.create(name='Computer Science', code='CS', faculty=self.fac)
        self.prog = Program.objects.create(name='BSc CS', code='BSCS', department=self.dept)

        # create student user & profile
        u = User.objects.create_user('s1', 's1@example.com', 'pass')
        self.stud = Student.objects.create(user=u, student_id='S100', email='s1@example.com', faculty=self.fac, department=self.dept, program=self.prog)

        # create a lecturer for uploaded_by (optional)
        lu = User.objects.create_user('lec', 'lec@example.com', 'pass')
        self.lect = Lecturer.objects.create(user=lu, lecturer_id='L1', email='lec@example.com')

        # create a published result
        self.result = Result.objects.create(
            student=self.stud,
            program=self.prog,
            department=self.dept,
            faculty=self.fac,
            subject='Intro to CS',
            result_type='exam',
            score=85.0,
            total_score=100.0,
            grade='A',
            academic_year='2024/2025',
            semester='1',
            uploaded_by=self.lect,
            is_published=True
        )

    def test_export_csv_returns_attachment(self):
        url = reverse('export_results_csv')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp['Content-Type'].startswith('text/csv'))
        content = resp.content.decode('utf-8')
        self.assertIn('student_id,student_name,faculty,department,program', content)
        self.assertIn('S100', content)

    def test_archive_program_results_creates_folders(self):
        url = reverse('archive_program_results')
        resp = self.client.post(url, {'program_id': self.prog.id, 'academic_year': '2024/2025', 'semester': '1'})
        # should redirect back
        self.assertIn(resp.status_code, (302, 200))

        folders = StudentSemesterFolder.objects.filter(student=self.stud, academic_year='2024/2025', semester='1')
        self.assertTrue(folders.exists())
        folder = folders.first()
        # result should be attached to folder
        self.result.refresh_from_db()
        self.assertEqual(self.result.folder, folder)
