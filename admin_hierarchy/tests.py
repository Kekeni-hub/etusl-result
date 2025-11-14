from django.test import TestCase, Client
from django.contrib.auth.models import User
from student.models import Faculty, Department
from .models import DeanOfFaculty

class DeanDashboardAccessTest(TestCase):
    def setUp(self):
        # Create faculty and department
        self.faculty, _ = Faculty.objects.get_or_create(name='TestFaculty', code='TF')
        self.department, _ = Department.objects.get_or_create(name='TestDept', code='TD', faculty=self.faculty)
        # Create dean user
        self.dean_username = 'test_dean'
        self.dean_password = 'TestDeanPass123!'
        self.user = User.objects.create_user(username=self.dean_username, email='dean@test.local', password=self.dean_password, first_name='Test', last_name='Dean')
        DeanOfFaculty.objects.create(user=self.user, dean_id='DEANTEST001', email='dean@test.local', faculty=self.faculty, is_active=True)
        self.client = Client()

    def test_dean_dashboard_requires_login(self):
        # Without login should redirect to login
        response = self.client.get('/admin-hierarchy/dean/dashboard/', follow=True)
        # Should not include dean context when not authenticated
        self.assertIsNone(response.context.get('dean'))

    def test_dean_dashboard_with_login(self):
        login = self.client.login(username=self.dean_username, password=self.dean_password)
        self.assertTrue(login)
        response = self.client.get('/admin-hierarchy/dean/dashboard/')
        self.assertEqual(response.status_code, 200)
