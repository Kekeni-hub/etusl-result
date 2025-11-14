#!/usr/bin/env python
"""
End-to-End Workflow Chain Test
Tests: Lecturer → HOD → DEAN → EXAM Officer

Flow:
1. Lecturer submits student result
2. HOD approves and forwards to DEAN
3. DEAN approves and forwards to EXAM Officer
4. EXAM Officer publishes the result
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
django.setup()

from django.contrib.auth.models import User
from student.models import Student, Result, Faculty, Department, Program
from lecturer.models import Lecturer
from admin_hierarchy.models import HeadOfDepartment, DeanOfFaculty, ResultApprovalWorkflow, ApprovalHistory
from exam_officer.models import ExamOfficer
from django.utils import timezone

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_workflow():
    print_section("WORKFLOW CHAIN TEST: Lecturer → HOD → DEAN → EXAM Officer")
    
    try:
        # Step 1: Get test accounts
        print("STEP 1: Retrieving test accounts...")
        lecturer = Lecturer.objects.filter(is_active=True).first()
        hod = HeadOfDepartment.objects.filter(is_active=True).first()
        dean = DeanOfFaculty.objects.filter(is_active=True).first()
        exam_officer = ExamOfficer.objects.filter(is_active=True).first()
        
        if not all([lecturer, hod, dean, exam_officer]):
            print("ERROR: Missing test accounts!")
            return False
        
        print(f"OK Lecturer: {lecturer.user.get_full_name()}")
        print(f"OK HOD: {hod.user.get_full_name()}")
        print(f"OK DEAN: {dean.user.get_full_name()}")
        print(f"OK EXAM Officer: {exam_officer.user.get_full_name()}")
        
        # Step 2: Get or create test student
        print_section("STEP 2: Getting or creating test student...")
        student = Student.objects.filter(is_active=True, department=hod.department).first()
        if not student:
            print("Creating new test student...")
            test_user = User.objects.create_user(
                username=f'teststudent_{int(timezone.now().timestamp())}',
                email=f'teststudent_{int(timezone.now().timestamp())}@example.local',
                first_name='Test',
                last_name='Student',
                password='TestPass123!'
            )
            program = Program.objects.filter(department=hod.department).first()
            if not program:
                program = Program.objects.create(
                    name="Test Program",
                    code="TESTPROG",
                    department=hod.department
                )
            student = Student.objects.create(
                user=test_user,
                student_id=f'TESTSTD{int(timezone.now().timestamp())}',
                email=test_user.email,
                faculty=hod.department.faculty,
                department=hod.department,
                program=program,
                current_year=1,
                is_active=True,
            )
        print(f"OK Student: {student.user.get_full_name()} ({student.student_id})")
        
        # Step 3: Create a result as Lecturer
        print_section("STEP 3: Lecturer submitting result...")
        program = student.program or Program.objects.filter(department=student.department).first()
        result, created = Result.objects.update_or_create(
            student=student,
            subject='Test Subject - Workflow Test',
            result_type='exam',
            academic_year='2024/2025',
            semester='1',
            defaults={
                'program': program,
                'department': student.department,
                'faculty': student.faculty,
                'score': 85,
                'total_score': 100,
                'grade': 'A',
                'uploaded_by': lecturer,
            }
        )
        print(f"OK Result: {result.score}/{result.total_score} (Grade: {result.grade})")
        
        # Step 4: Create workflow
        print_section("STEP 4: Workflow created (Lecturer Submitted)...")
        workflow, created = ResultApprovalWorkflow.objects.update_or_create(
            result=result,
            defaults={
                'status': 'lecturer_submitted',
                'current_hod': hod,
            }
        )
        print(f"OK Workflow Status: {workflow.get_status_display()}")
        print(f"OK Current HOD: {workflow.current_hod.user.get_full_name()}")
        
        # Step 5: HOD approves
        print_section("STEP 5: HOD approving and forwarding to DEAN...")
        workflow.status = 'hod_approved'
        workflow.hod_notes = 'Scores verified. Forwarding to DEAN.'
        workflow.hod_reviewed_at = timezone.now()
        workflow.current_dean = dean
        workflow.save()
        ApprovalHistory.objects.create(
            workflow=workflow,
            action='hod_approved',
            admin_user=hod.user,
            notes=workflow.hod_notes
        )
        print(f"OK Workflow Status: {workflow.get_status_display()}")
        print(f"OK Current DEAN: {workflow.current_dean.user.get_full_name()}")
        
        # Step 6: DEAN approves
        print_section("STEP 6: DEAN approving and forwarding to EXAM Officer...")
        workflow.status = 'dean_approved'
        workflow.dean_notes = 'Verified by faculty. Ready for publication.'
        workflow.dean_reviewed_at = timezone.now()
        workflow.current_exam_officer = exam_officer
        workflow.save()
        ApprovalHistory.objects.create(
            workflow=workflow,
            action='dean_approved',
            admin_user=dean.user,
            notes=workflow.dean_notes
        )
        print(f"OK Workflow Status: {workflow.get_status_display()}")
        print(f"OK Current EXAM Officer: {workflow.current_exam_officer.user.get_full_name()}")
        
        # Step 7: EXAM Officer publishes
        print_section("STEP 7: EXAM Officer publishing result...")
        result.is_published = True
        result.published_date = timezone.now()
        result.save()
        workflow.status = 'exam_published'
        workflow.exam_reviewed_at = timezone.now()
        workflow.exam_notes = 'Published by EXAM Officer.'
        workflow.save()
        ApprovalHistory.objects.create(
            workflow=workflow,
            action='exam_published',
            admin_user=exam_officer.user,
            notes=workflow.exam_notes
        )
        print(f"OK Workflow Status: {workflow.get_status_display()}")
        print(f"OK Result Published: {result.is_published}")
        
        # Summary
        print_section("SUCCESS: WORKFLOW CHAIN COMPLETE")
        print("Approval History:")
        for i, hist in enumerate(workflow.history.all().order_by('created_at'), 1):
            print(f"{i}. {hist.get_action_display()} by {hist.admin_user.get_full_name()}")
        
        print("\n" + "="*70)
        print("TEST PASSED!")
        print("Grades flow successfully through: Lecturer → HOD → DEAN → EXAM Officer")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_workflow()
    sys.exit(0 if success else 1)
