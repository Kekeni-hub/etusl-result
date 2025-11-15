from django.test import TestCase, Client
from django.contrib.auth.models import User
from student.models import Faculty, Department, Program, Student, Result
from django.urls import reverse
from django.utils import timezone

class DownloadResultTests(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(name='DF', code='DF')
        self.department = Department.objects.create(name='DD', code='DD', faculty=self.faculty)
        self.program = Program.objects.create(name='DP', code='DP', department=self.department)

        self.user = User.objects.create_user(username='stu1', password='pass')
        self.student = Student.objects.create(user=self.user, student_id='ST1', email='st1@example.com', department=self.department, program=self.program, faculty=self.faculty)

        # result with published_date
        self.result_with_date = Result.objects.create(student=self.student, subject='R1', result_type='exam', score=70, total_score=100, grade='B', academic_year='2024/2025', semester='1', program=self.program, department=self.department, faculty=self.faculty, is_published=True, published_date=timezone.now())
        # result without published_date
        self.result_no_date = Result.objects.create(student=self.student, subject='R2', result_type='exam', score=60, total_score=100, grade='C', academic_year='2024/2025', semester='1', program=self.program, department=self.department, faculty=self.faculty, is_published=True, published_date=None)

        self.client = Client(SERVER_NAME='127.0.0.1')
        self.client.force_login(self.user)

    def test_download_with_published_date(self):
        url = reverse('download_result', args=[self.result_with_date.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Content-Disposition', resp)
        content = resp.content.decode()
        self.assertIn('STUDENT RESULT', content.upper())

    def test_download_without_published_date(self):
        url = reverse('download_result', args=[self.result_no_date.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('N/A', resp.content.decode())
