"""
Django signals for automatic notification sending in the results workflow.
Notifications are sent when results move through different approval stages.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from admin_hierarchy.models import ResultApprovalWorkflow, HeadOfDepartment, DeanOfFaculty
from exam_officer.models import Notification
from student.models import Result, Student
from lecturer.models import Lecturer


def notify_hod_approved(workflow):
    """Notify DEAN when HOD approves a result"""
    if workflow.current_dean and workflow.current_dean.user:
        Notification.objects.create(
            recipient=workflow.current_dean.user,
            notification_type='hod_approved',
            title='Result Approved by HOD',
            message=f'HOD has approved result for student {workflow.result.student.student_id} in {workflow.result.subject}. Please review and approve.',
            workflow=workflow,
            result=workflow.result,
        )


def notify_hod_rejected(workflow):
    """Notify LECTURER when HOD rejects a result"""
    if workflow.result.uploaded_by and workflow.result.uploaded_by.user:
        Notification.objects.create(
            recipient=workflow.result.uploaded_by.user,
            notification_type='hod_rejected',
            title='Result Rejected by HOD',
            message=f'Your result submission for student {workflow.result.student.student_id} in {workflow.result.subject} has been rejected by HOD. Please review and resubmit.',
            workflow=workflow,
            result=workflow.result,
        )


def notify_dean_approved(workflow):
    """Notify EXAM OFFICER when DEAN approves a result"""
    if workflow.current_exam_officer and workflow.current_exam_officer.user:
        Notification.objects.create(
            recipient=workflow.current_exam_officer.user,
            notification_type='dean_approved',
            title='Result Approved by Dean',
            message=f'Dean has approved result for student {workflow.result.student.student_id} in {workflow.result.subject}. Ready for publication.',
            workflow=workflow,
            result=workflow.result,
        )


def notify_dean_rejected(workflow):
    """Notify HOD when DEAN rejects a result"""
    if workflow.current_hod and workflow.current_hod.user:
        Notification.objects.create(
            recipient=workflow.current_hod.user,
            notification_type='dean_rejected',
            title='Result Rejected by Dean',
            message=f'Dean has rejected result for student {workflow.result.student.student_id} in {workflow.result.subject}. Please review and resubmit.',
            workflow=workflow,
            result=workflow.result,
        )


def notify_student_results_published(workflow):
    """Notify STUDENT when their results are published"""
    student_user = workflow.result.student.user
    if student_user:
        Notification.objects.create(
            recipient=student_user,
            notification_type='result',
            title='Your Results Have Been Published',
            message=f'Your result for {workflow.result.subject} has been published. You can now view your grade.',
            workflow=workflow,
            result=workflow.result,
        )


def notify_department_results_published(workflow):
    """Notify HOD when department results are published"""
    if workflow.current_hod and workflow.current_hod.user:
        Notification.objects.create(
            recipient=workflow.current_hod.user,
            notification_type='result',
            title='Department Results Published',
            message=f'Result for student {workflow.result.student.student_id} in {workflow.result.subject} has been published.',
            workflow=workflow,
            result=workflow.result,
        )


def notify_faculty_results_published(workflow):
    """Notify DEAN when faculty results are published"""
    if workflow.current_dean and workflow.current_dean.user:
        Notification.objects.create(
            recipient=workflow.current_dean.user,
            notification_type='result',
            title='Faculty Results Published',
            message=f'Result for student {workflow.result.student.student_id} in {workflow.result.subject} has been published.',
            workflow=workflow,
            result=workflow.result,
        )

