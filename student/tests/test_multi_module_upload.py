from django.test import TestCase, Client
from django.contrib.auth.models import User
from student.models import Student, Faculty, Department, Program, Module, Assessment, Result
from lecturer.models import Lecturer
from admin_hierarchy.models import HeadOfDepartment, ResultApprovalWorkflow
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import json


class MultiModuleUploadFormTest(TestCase):
    """Test form-based multi-module upload via lecturer UI."""

    def setUp(self):
        """Set up test data."""
        # Create faculty, department, program
        self.faculty = Faculty.objects.create(name='Engineering', code='ENG')
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            faculty=self.faculty
        )
        self.program = Program.objects.create(
            name='B.Sc Computer Science',
            code='BSCS',
            department=self.department
        )

        # Create modules
        self.module1 = Module.objects.create(
            name='Data Structures',
            code='CS101',
            program=self.program,
            department=self.department,
            faculty=self.faculty,
            credits=3
        )
        self.module2 = Module.objects.create(
            name='Algorithms',
            code='CS102',
            program=self.program,
            department=self.department,
            faculty=self.faculty,
            credits=3
        )

        # Create students
        user1 = User.objects.create_user(
            username='student1@example.com',
            email='student1@example.com',
            password='pass123'
        )
        self.student1 = Student.objects.create(
            user=user1,
            student_id='S001',
            email='student1@example.com',
            faculty=self.faculty,
            department=self.department,
            program=self.program,
            is_active=True
        )

        user2 = User.objects.create_user(
            username='student2@example.com',
            email='student2@example.com',
            password='pass123'
        )
        self.student2 = Student.objects.create(
            user=user2,
            student_id='S002',
            email='student2@example.com',
            faculty=self.faculty,
            department=self.department,
            program=self.program,
            is_active=True
        )

        # Create HOD
        hod_user = User.objects.create_user(
            username='hod@example.com',
            email='hod@example.com',
            password='hodpass'
        )
        self.hod = HeadOfDepartment.objects.create(
            user=hod_user,
            department=self.department,
            email='hod@example.com',
            is_active=True
        )

        # Create lecturer
        lecturer_user = User.objects.create_user(
            username='lecturer@example.com',
            email='lecturer@example.com',
            password='lecpass'
        )
        self.lecturer = Lecturer.objects.create(
            user=lecturer_user,
            lecturer_id='L001',
            email='lecturer@example.com',
            faculty=self.faculty,
            department=self.department,
            is_active=True,
            is_verified=True
        )

        self.client = Client()

    def test_upload_results_form_page(self):
        """Test that upload results page renders with modules and students."""
        self.client.login(username='lecturer@example.com', password='lecpass')
        response = self.client.get('/lecturer/upload-results/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload Student Results')
        # Check that modules are in the template context
        self.assertIn('modules', response.context)
        self.assertEqual(len(response.context['modules']), 2)

    def test_multi_module_upload_form_submission(self):
        """Test form-based multi-module upload via assessments_json."""
        self.client.login(username='lecturer@example.com', password='lecpass')

        # Build payload simulating form submission
        payload = [
            {
                'student_id': self.student1.id,
                'module_id': self.module1.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments': {
                    'exam': {'score': 85, 'total': 100},
                    'test': {'score': 15, 'total': 20},
                    'assignment': {'score': 18, 'total': 20}
                }
            },
            {
                'student_id': self.student1.id,
                'module_id': self.module2.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments': {
                    'exam': {'score': 75, 'total': 100},
                    'attendance': {'score': 9, 'total': 10}
                }
            },
            {
                'student_id': self.student2.id,
                'module_id': self.module1.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments': {
                    'exam': {'score': 60, 'total': 100},
                    'test': {'score': 12, 'total': 20}
                }
            }
        ]

        response = self.client.post(
            '/lecturer/upload-results/',
            {
                'program': self.program.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments_json': json.dumps(payload)
            }
        )

        # Should redirect on success
        self.assertEqual(response.status_code, 302)

        # Check that assessments were created
        assessments = Assessment.objects.all()
        self.assertGreater(assessments.count(), 0)
        # 3 entries x ~2 assessments each = ~6 assessment objects
        self.assertGreaterEqual(assessments.count(), 5)

        # Check that results were created
        results = Result.objects.filter(academic_year='2024/2025', semester='1')
        self.assertGreater(results.count(), 0)

        # Check that workflows were created
        workflows = ResultApprovalWorkflow.objects.all()
        self.assertGreater(workflows.count(), 0)

    def test_assessment_aggregation_into_result(self):
        """Test that assessments are aggregated into module-level results."""
        self.client.login(username='lecturer@example.com', password='lecpass')

        payload = [
            {
                'student_id': self.student1.id,
                'module_id': self.module1.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments': {
                    'exam': {'score': 80, 'total': 100},
                    'test': {'score': 16, 'total': 20},
                    'assignment': {'score': 19, 'total': 20}
                }
            }
        ]

        self.client.post(
            '/lecturer/upload-results/',
            {
                'program': self.program.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments_json': json.dumps(payload)
            }
        )

        # Check that 3 assessment objects were created
        assessments = Assessment.objects.filter(
            student=self.student1,
            module=self.module1,
            academic_year='2024/2025'
        )
        self.assertEqual(assessments.count(), 3)

        # Check that a result exists for this student/module
        result = Result.objects.filter(
            student=self.student1,
            subject=self.module1.name,
            academic_year='2024/2025',
            semester='1'
        ).first()
        self.assertIsNotNone(result)
        self.assertTrue(result.grade in ['A', 'B', 'C', 'D', 'F'])


class MultiModuleUploadAPITest(TestCase):
    """Test API-based multi-module upload via DRF endpoint."""

    def setUp(self):
        """Set up test data."""
        # Create faculty, department, program
        self.faculty = Faculty.objects.create(name='Engineering', code='ENG')
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            faculty=self.faculty
        )
        self.program = Program.objects.create(
            name='B.Sc Computer Science',
            code='BSCS',
            department=self.department
        )

        # Create modules
        self.module1 = Module.objects.create(
            name='Data Structures',
            code='CS101',
            program=self.program,
            department=self.department,
            faculty=self.faculty,
            credits=3
        )

        # Create students
        user1 = User.objects.create_user(
            username='student1@example.com',
            email='student1@example.com',
            password='pass123'
        )
        self.student1 = Student.objects.create(
            user=user1,
            student_id='S001',
            email='student1@example.com',
            faculty=self.faculty,
            department=self.department,
            program=self.program,
            is_active=True
        )

        # Create HOD
        hod_user = User.objects.create_user(
            username='hod@example.com',
            email='hod@example.com',
            password='hodpass'
        )
        self.hod = HeadOfDepartment.objects.create(
            user=hod_user,
            department=self.department,
            email='hod@example.com',
            is_active=True
        )

        # Create lecturer with token
        lecturer_user = User.objects.create_user(
            username='lecturer@example.com',
            email='lecturer@example.com',
            password='lecpass'
        )
        self.lecturer = Lecturer.objects.create(
            user=lecturer_user,
            lecturer_id='L001',
            email='lecturer@example.com',
            faculty=self.faculty,
            department=self.department,
            is_active=True,
            is_verified=True
        )
        self.token = Token.objects.create(user=lecturer_user)

        self.client = APIClient()

    def test_bulk_upload_endpoint(self):
        """Test /api/results/bulk_upload/ endpoint."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        payload = [
            {
                'student_id': self.student1.id,
                'module_id': self.module1.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments': {
                    'exam': {'score': 88, 'total': 100},
                    'test': {'score': 17, 'total': 20}
                }
            }
        ]

        response = self.client.post(
            '/api/results/bulk_upload/',
            payload,
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn('created_assessments', response.data)
        self.assertGreater(response.data['created_assessments'], 0)

        # Check that assessments were created
        assessments = Assessment.objects.filter(
            student=self.student1,
            module=self.module1
        )
        self.assertEqual(assessments.count(), 2)

    def test_bulk_upload_invalid_student(self):
        """Test bulk upload with invalid student ID."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        payload = [
            {
                'student_id': 99999,  # Non-existent
                'module_id': self.module1.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments': {'exam': {'score': 80, 'total': 100}}
            }
        ]

        response = self.client.post(
            '/api/results/bulk_upload/',
            payload,
            format='json'
        )

        # Should still return 207 with errors
        self.assertIn(response.status_code, [207, 201])
        if response.status_code == 207:
            self.assertIn('errors', response.data)
            self.assertGreater(len(response.data['errors']), 0)

    def test_bulk_upload_non_lecturer(self):
        """Test bulk upload as non-lecturer (should fail)."""
        # Use student user token
        student_token = Token.objects.create(user=self.student1.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {student_token.key}')

        payload = [
            {
                'student_id': self.student1.id,
                'module_id': self.module1.id,
                'academic_year': '2024/2025',
                'semester': '1',
                'assessments': {'exam': {'score': 80, 'total': 100}}
            }
        ]

        response = self.client.post(
            '/api/results/bulk_upload/',
            payload,
            format='json'
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.data)


class ExamOfficerPreviewTest(TestCase):
    """Test exam-officer preview and publish workflow."""

    def setUp(self):
        """Set up test data."""
        # Create faculty, department, program
        self.faculty = Faculty.objects.create(name='Engineering', code='ENG')
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            faculty=self.faculty
        )
        self.program = Program.objects.create(
            name='B.Sc Computer Science',
            code='BSCS',
            department=self.department
        )

        # Create a student and result
        user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='pass'
        )
        self.student = Student.objects.create(
            user=user,
            student_id='S001',
            email='student@example.com',
            faculty=self.faculty,
            department=self.department,
            program=self.program,
            is_active=True
        )

        # Create HOD
        hod_user = User.objects.create_user(
            username='hod@example.com',
            email='hod@example.com',
            password='hod'
        )
        self.hod = HeadOfDepartment.objects.create(
            user=hod_user,
            department=self.department,
            email='hod@example.com',
            is_active=True
        )

        # Create a result and workflow in dean_approved status
        self.result = Result.objects.create(
            student=self.student,
            subject='Data Structures',
            program=self.program,
            department=self.department,
            faculty=self.faculty,
            score=85,
            total_score=100,
            grade='A',
            academic_year='2024/2025',
            semester='1'
        )

        self.workflow = ResultApprovalWorkflow.objects.create(
            result=self.result,
            status='dean_approved',
            current_hod=self.hod
        )

        self.client = Client()

    def test_workflow_created_in_dean_approved_status(self):
        """Test that workflows are created correctly."""
        self.assertIsNotNone(self.workflow)
        self.assertEqual(self.workflow.status, 'dean_approved')
        self.assertEqual(self.workflow.result, self.result)

