from django.test import TestCase, Client
from django.contrib.auth.models import User
from student.models import Faculty, Department, Program, Student, Result
from admin_hierarchy.models import ResultApprovalWorkflow, ApprovalHistory
from exam_officer.models import ExamOfficer
from django.urls import reverse
from django.utils import timezone

class PublishWorkflowTests(TestCase):
    def setUp(self):
        # create faculty/department/program
        self.faculty = Faculty.objects.create(name='TFac', code='TF')
        self.department = Department.objects.create(name='TDept', code='TD', faculty=self.faculty)
        self.program = Program.objects.create(name='TProg', code='TP', department=self.department)

        # create users
        self.exam_user = User.objects.create_user(username='examuser', password='pass')
        self.exam_officer = ExamOfficer.objects.create(user=self.exam_user, officer_id='EO1', email='eo@example.com')

        self.student_user = User.objects.create_user(username='student1', password='pass')
        self.student = Student.objects.create(user=self.student_user, student_id='S1', email='s1@example.com', department=self.department, program=self.program, faculty=self.faculty)

        # create result and workflow
        self.result = Result.objects.create(student=self.student, subject='Sub', result_type='exam', score=80, total_score=100, grade='A', academic_year='2024/2025', semester='1', program=self.program, department=self.department, faculty=self.faculty, is_published=False)
        self.workflow = ResultApprovalWorkflow.objects.create(result=self.result, status='dean_approved', dean_reviewed_at=timezone.now())

        self.client = Client(SERVER_NAME='127.0.0.1')
        self.client.force_login(self.exam_user)

    def test_publish_result_changes_status_and_creates_history(self):
        url = reverse('exam_officer_publish_result', args=[self.workflow.id])
        resp = self.client.post(url, {'action':'publish', 'notes':'ok'}, follow=True)
        self.assertNotEqual(resp.status_code, 500)
        # reload workflow
        wf = ResultApprovalWorkflow.objects.get(id=self.workflow.id)
        self.assertEqual(wf.status, 'exam_published')
        # history entry
        history = ApprovalHistory.objects.filter(workflow=wf, action='exam_published')
        self.assertTrue(history.exists())

    def test_return_result_sets_exam_returned_and_history(self):
        url = reverse('exam_officer_publish_result', args=[self.workflow.id])
        resp = self.client.post(url, {'action':'return', 'notes':'needs work'}, follow=True)
        self.assertNotEqual(resp.status_code, 500)
        wf = ResultApprovalWorkflow.objects.get(id=self.workflow.id)
        # return sets status back to dean_approved in view; history should have exam_returned
        self.assertEqual(wf.status, 'dean_approved')
        history = ApprovalHistory.objects.filter(workflow=wf, action='exam_returned')
        self.assertTrue(history.exists())
