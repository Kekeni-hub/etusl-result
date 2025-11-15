from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from student.models import Student, Faculty, Department, Program


class StudentLoginFlowsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # create minimal faculty/department/program
        self.faculty = Faculty.objects.create(name='Test Faculty', code='TF')
        self.department = Department.objects.create(name='Test Dept', code='TD', faculty=self.faculty)
        self.program = Program.objects.create(name='Test Program', code='TP', department=self.department)

        # create a user and student as dean would
        self.temporary_password = 'TempPass123!'
        self.user = User.objects.create_user(username='student1@example.com', email='student1@example.com', first_name='John', last_name='Doe', password=self.temporary_password)
        self.student = Student.objects.create(
            user=self.user,
            student_id='S1001',
            email='student1@example.com',
            faculty=self.faculty,
            department=self.department,
            program=self.program,
            current_year=1,
            is_active=True,
            must_change_password=True
        )

    def test_password_login_forced_change(self):
        # login with password should redirect to force password change
        resp = self.client.post(reverse('student_login'), {'student_id': 'S1001', 'password': self.temporary_password})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('student_force_password_change'), resp.url)

        # follow and set new password
        # login via client then post to change
        self.client.login(username=self.user.username, password=self.temporary_password)
        resp2 = self.client.post(reverse('student_force_password_change'), {'new_password': 'NewPass!234', 'confirm_password': 'NewPass!234'})
        self.assertEqual(resp2.status_code, 302)
        # refreshed student flag should be False
        self.student.refresh_from_db()
        self.assertFalse(self.student.must_change_password)

    def test_info_based_login(self):
        # unset must_change_password for this test
        self.student.must_change_password = False
        self.student.save()
        resp = self.client.post(reverse('student_login'), {'student_id': 'S1001', 'name': 'John', 'email': 'student1@example.com'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('student_dashboard'), resp.url)