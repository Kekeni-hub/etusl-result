from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Etu_student_result.decorators import require_profile
from Etu_student_result.security_utils import InputValidator, InputSanitizer, LogSecurity
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
import csv, io, logging
from student.models import Faculty, Department, Program, StudentSemesterFolder
from django.urls import reverse

from .models import HeadOfDepartment, DeanOfFaculty, ResultApprovalWorkflow, ApprovalHistory
from student.models import Student, Result, Department, Faculty, Program
from exam_officer.models import ExamOfficer
from .forms import DeanStudentForm
from .forms import DeanProgramForm

logger = logging.getLogger('security')


def hod_index(request):
    """Redirect /hod/ to dashboard or login"""
    if request.user.is_authenticated and hasattr(request.user, 'hod_profile'):
        return redirect('hod_dashboard')
    return redirect('hod_login')


def dean_index(request):
    """Redirect /dean/ to dashboard or login"""
    if request.user.is_authenticated and hasattr(request.user, 'dean_profile'):
        return redirect('dean_dashboard')
    return redirect('dean_login')


@require_http_methods(["GET", "POST"])
def hod_login(request):
    """HOD (Head of Department) login"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'hod_profile'):
            return redirect('hod_dashboard')
    
    if request.method == 'POST':
        identifier = request.POST.get('identifier') or request.POST.get('email')
        password = request.POST.get('password')

        user = None
        if identifier:
            if '@' in identifier:
                try:
                    hod = HeadOfDepartment.objects.get(email__iexact=identifier)
                    user = hod.user
                except HeadOfDepartment.DoesNotExist:
                    user = User.objects.filter(email__iexact=identifier).first()
            else:
                user = User.objects.filter(username__iexact=identifier).first()

        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                try:
                    hod = HeadOfDepartment.objects.get(user=user)
                    if not hod.is_active:
                        messages.error(request, 'Your account has been deactivated.')
                        return redirect('hod_login')
                except HeadOfDepartment.DoesNotExist:
                    messages.error(request, 'HOD profile not found.')
                    return redirect('hod_login')

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome, HOD {user.first_name}!')
                return redirect('hod_dashboard')
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'admin_hierarchy/hod_login.html')


@require_profile('hod_profile', login_url='hod_login')
def hod_dashboard(request):
    """HOD dashboard - view pending submissions and manage students"""
    try:
        hod = request.user.hod_profile
    except:
        return redirect('hod_login')
    
    # Get pending workflows for this HOD's department
    pending_workflows = ResultApprovalWorkflow.objects.filter(
        current_hod=hod,
        status='lecturer_submitted'
        ).select_related('result__student')
    
    # Get HOD-approved but not yet sent to DEAN
    approved_by_hod = ResultApprovalWorkflow.objects.filter(
        current_hod=hod,
        status='hod_approved'
        ).select_related('result__student')
    
    # Students in this HOD's department
    students = Student.objects.filter(department=hod.department, is_active=True)
    
    context = {
        'hod': hod,
        'pending_count': pending_workflows.count(),
        'approved_count': approved_by_hod.count(),
        'pending_workflows': pending_workflows[:10],
        'approved_workflows': approved_by_hod[:10],
        'students': students[:20],
    }
    
    return render(request, 'admin_hierarchy/hod_dashboard.html', context)


@require_profile('hod_profile', login_url='hod_login')
def hod_pending_list(request):
    """Dedicated page showing all pending submissions for the HOD's department"""
    try:
        hod = request.user.hod_profile
    except:
        return redirect('hod_login')

    q = request.GET.get('q', '').strip()
    pending_qs = ResultApprovalWorkflow.objects.filter(
        current_hod=hod,
        status='lecturer_submitted'
    ).select_related('result__student')

    if q:
        pending_qs = pending_qs.filter(
            Q(result__student__student_id__icontains=q) |
            Q(result__subject__icontains=q)
        )

    paginator = Paginator(pending_qs, 20)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    context = {
        'hod': hod,
        'pending_page': page,
        'q': q,
    }
    return render(request, 'admin_hierarchy/hod_pending.html', context)


@require_profile('hod_profile', login_url='hod_login')
def hod_approved_list(request):
    """Dedicated page showing all HOD-approved submissions for the HOD's department"""
    try:
        hod = request.user.hod_profile
    except:
        return redirect('hod_login')

    q = request.GET.get('q', '').strip()
    approved_qs = ResultApprovalWorkflow.objects.filter(
        current_hod=hod,
        status='hod_approved'
    ).select_related('result__student')

    if q:
        approved_qs = approved_qs.filter(
            Q(result__student__student_id__icontains=q) |
            Q(result__subject__icontains=q)
        )

    paginator = Paginator(approved_qs, 20)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    context = {
        'hod': hod,
        'approved_page': page,
        'q': q,
    }
    return render(request, 'admin_hierarchy/hod_approved.html', context)



@login_required(login_url='hod_login')
def hod_review_result(request, workflow_id):
    """HOD reviews a result submission and approves/rejects"""
    try:
        hod = request.user.hod_profile
    except:
        return redirect('hod_login')
    
    workflow = get_object_or_404(ResultApprovalWorkflow, id=workflow_id, current_hod=hod)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            workflow.status = 'hod_approved'
            workflow.hod_notes = notes
            workflow.hod_reviewed_at = timezone.now()
            # Assign to DEAN
            dean = DeanOfFaculty.objects.get(faculty=hod.department.faculty)
            workflow.current_dean = dean
            workflow.save()
            
            # Log action
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='hod_approved',
                admin_user=request.user,
                notes=notes
            )
            
            # Send notification to DEAN
            from admin_hierarchy.signals import notify_hod_approved
            notify_hod_approved(workflow)
            
            messages.success(request, 'Result approved by HOD. Forwarded to DEAN.')
        
        elif action == 'reject':
            workflow.status = 'hod_rejected'
            workflow.hod_notes = notes
            workflow.hod_reviewed_at = timezone.now()
            workflow.save()
            
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='hod_rejected',
                admin_user=request.user,
                notes=notes
            )
            
            # Send notification to lecturer
            from admin_hierarchy.signals import notify_hod_rejected
            notify_hod_rejected(workflow)
            
            messages.warning(request, 'Result rejected by HOD. Lecturer will be notified.')
        
        return redirect('hod_dashboard')
    
    context = {
        'workflow': workflow,
        'result': workflow.result,
        'student': workflow.result.student,
    }
    
    return render(request, 'admin_hierarchy/hod_review_result.html', context)


@require_http_methods(["GET", "POST"])
def dean_login(request):
    """DEAN (Faculty Admin) login"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'dean_profile'):
            return redirect('dean_dashboard')
    
    if request.method == 'POST':
        identifier = request.POST.get('identifier') or request.POST.get('email')
        password = request.POST.get('password')

        user = None
        if identifier:
            if '@' in identifier:
                try:
                    dean = DeanOfFaculty.objects.get(email__iexact=identifier)
                    user = dean.user
                except DeanOfFaculty.DoesNotExist:
                    user = User.objects.filter(email__iexact=identifier).first()
            else:
                user = User.objects.filter(username__iexact=identifier).first()

        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                try:
                    dean = DeanOfFaculty.objects.get(user=user)
                    if not dean.is_active:
                        messages.error(request, 'Your account has been deactivated.')
                        return redirect('dean_login')
                except DeanOfFaculty.DoesNotExist:
                    messages.error(request, 'DEAN profile not found.')
                    return redirect('dean_login')

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome, DEAN {user.first_name}!')
                return redirect('dean_dashboard')
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'admin_hierarchy/dean_login.html')


@require_profile('dean_profile', login_url='dean_login')
def dean_dashboard(request):
    """DEAN dashboard - review HOD approvals"""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')
    
    # Get pending workflows for this DEAN's faculty
    pending_qs = ResultApprovalWorkflow.objects.filter(
        current_dean=dean,
        status='hod_approved'
    ).select_related('result__student', 'current_hod')

    # Get DEAN-approved but not yet sent to EXAM
    approved_qs = ResultApprovalWorkflow.objects.filter(
        current_dean=dean,
        status='dean_approved'
    ).select_related('result__student')

    # Filtering (search) by student id or subject
    q = request.GET.get('q', '').strip()
    if q:
        pending_qs = pending_qs.filter(
            Q(result__student__student_id__icontains=q) |
            Q(result__subject__icontains=q)
        )
        approved_qs = approved_qs.filter(
            Q(result__student__student_id__icontains=q) |
            Q(result__subject__icontains=q)
        )

    # Paginate both lists (10 per page)
    pending_page_number = request.GET.get('pending_page', 1)
    approved_page_number = request.GET.get('approved_page', 1)

    pending_paginator = Paginator(pending_qs, 10)
    approved_paginator = Paginator(approved_qs, 10)

    try:
        pending_page = pending_paginator.get_page(pending_page_number)
    except:
        pending_page = pending_paginator.get_page(1)

    try:
        approved_page = approved_paginator.get_page(approved_page_number)
    except:
        approved_page = approved_paginator.get_page(1)
    
    context = {
        'dean': dean,
        'pending_count': pending_qs.count(),
        'approved_count': approved_qs.count(),
        'pending_page': pending_page,
        'approved_page': approved_page,
        'q': q,
        # Extra counts for dashboard widgets
        'hod_count': HeadOfDepartment.objects.filter(department__faculty=dean.faculty).count(),
        'total_count': Result.objects.filter(faculty=dean.faculty).count(),
    }
    
    return render(request, 'admin_hierarchy/dean_dashboard.html', context)


@require_profile('dean_profile', login_url='dean_login')
def dean_pending_list(request):
    """Dedicated page showing all pending workflows for the DEAN's faculty"""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')

    q = request.GET.get('q', '').strip()
    pending_qs = ResultApprovalWorkflow.objects.filter(
        current_dean=dean,
        status='hod_approved'
    ).select_related('result__student', 'current_hod')

    if q:
        pending_qs = pending_qs.filter(
            Q(result__student__student_id__icontains=q) |
            Q(result__subject__icontains=q)
        )

    paginator = Paginator(pending_qs, 20)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    context = {
        'dean': dean,
        'pending_page': page,
        'q': q,
    }
    return render(request, 'admin_hierarchy/dean_pending.html', context)


@require_profile('dean_profile', login_url='dean_login')
def dean_finalized_list(request):
    """Dedicated page showing all finalized/DEAN-approved workflows for the DEAN's faculty"""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')

    q = request.GET.get('q', '').strip()
    approved_qs = ResultApprovalWorkflow.objects.filter(
        current_dean=dean,
        status='dean_approved'
    ).select_related('result__student', 'current_hod')

    if q:
        approved_qs = approved_qs.filter(
            Q(result__student__student_id__icontains=q) |
            Q(result__subject__icontains=q)
        )

    paginator = Paginator(approved_qs, 20)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    context = {
        'dean': dean,
        'approved_page': page,
        'q': q,
    }
    return render(request, 'admin_hierarchy/dean_finalized.html', context)


def faculties_list(request):
    faculties = Faculty.objects.all().order_by('name')
    return render(request, 'admin_hierarchy/faculties_list.html', {'faculties': faculties})


def faculty_detail(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    departments = Department.objects.filter(faculty=faculty).order_by('name')
    programs = Program.objects.filter(department__faculty=faculty).order_by('name')
    return render(request, 'admin_hierarchy/faculty_detail.html', {'faculty': faculty, 'departments': departments, 'programs': programs})


def department_detail(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id)
    programs = Program.objects.filter(department=dept).order_by('name')
    return render(request, 'admin_hierarchy/department_detail.html', {'department': dept, 'programs': programs})


@login_required(login_url='dean_login')
def dean_add_student(request):
    """Allow DEAN to add a student to their faculty; departments/programs limited to dean's faculty."""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')

    # Determine whether to show all departments/programs or restrict to dean's faculty
    show_all = request.GET.get('show_all') == '1' or request.POST.get('show_all') == '1'

    if request.method == 'POST':
        # Instantiate the form; respect the show_all toggle if provided
        form = DeanStudentForm(None if show_all else dean.faculty, request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            # Create the User
            from django.contrib.auth.models import User
            from django.utils.crypto import get_random_string
            from django.core.mail import send_mail
            from django.conf import settings

            # generate a temporary password
            password = get_random_string(10)
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=password
            )

            # Create the Student profile
            student = Student.objects.create(
                user=user,
                student_id=data['student_id'],
                email=data['email'],
                phone=data.get('phone', ''),
                faculty=dean.faculty,
                department=data['department'],
                program=data['program'],
                current_year=int(data['current_year']),
                date_of_birth=data.get('date_of_birth'),
                address=data.get('address', ''),
                is_active=True,
                must_change_password=True,
                photo=data.get('photo') or None
            )
            # send temporary password to student's email (console backend used in DEBUG)
            subject = 'Your student account has been created'
            message = (
                f"Hello {user.get_full_name()},\n\n"
                f"An account has been created for you at the Student Results portal.\n"
                f"Student ID: {student.student_id}\n"
                f"Temporary password: {password}\n\n"
                f"You will be required to change this password on first login.\n"
                f"Please login at: {request.build_absolute_uri(reverse('student_login'))}\n\n"
                f"Regards,\nUniversity Exams Office"
            )
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student.email], fail_silently=False)
                messages.success(request, f"Student {user.get_full_name()} ({student.student_id}) created and temporary password emailed to the student.")
            except Exception:
                # fallback: show a non-sensitive notification to dean
                messages.warning(request, f"Student {user.get_full_name()} ({student.student_id}) created. Failed to send email; please communicate the temporary password to the student securely.")
            return redirect('dean_dashboard')
    else:
        form = DeanStudentForm(None if show_all else dean.faculty)

    return render(request, 'admin_hierarchy/dean_add_student.html', {'form': form, 'dean': dean})


@login_required(login_url='dean_login')
def dean_add_program(request):
    """Allow DEAN to add a Program within their faculty (department must belong to their faculty)."""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')

    if request.method == 'POST':
        form = DeanProgramForm(dean.faculty, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            program = Program.objects.create(
                name=data['name'],
                code=data['code'],
                department=data['department'],
                description=data.get('description', '')
            )
            messages.success(request, f"Program '{program.name}' created under {program.department.name}.")
            return redirect('dean_dashboard')
    else:
        form = DeanProgramForm(dean.faculty)

    return render(request, 'admin_hierarchy/dean_add_program.html', {'form': form, 'dean': dean})


@login_required(login_url='dean_login')
def dean_review_result(request, workflow_id):
    """DEAN reviews HOD-approved results and forwards to EXAM"""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')
    
    workflow = get_object_or_404(ResultApprovalWorkflow, id=workflow_id, current_dean=dean)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            workflow.status = 'dean_approved'
            workflow.dean_notes = notes
            workflow.dean_reviewed_at = timezone.now()
            
            # Assign to an active EXAM Officer
            exam_officer = ExamOfficer.objects.filter(is_active=True).first()
            if exam_officer:
                workflow.current_exam_officer = exam_officer
            
            workflow.save()
            
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='dean_approved',
                admin_user=request.user,
                notes=notes
            )
            
            # Send notification to Exam Officer
            from admin_hierarchy.signals import notify_dean_approved
            notify_dean_approved(workflow)
            
            messages.success(request, 'Result approved by DEAN. Forwarded to EXAM officer for publication.')
        
        elif action == 'reject':
            workflow.status = 'dean_rejected'
            workflow.dean_notes = notes
            workflow.dean_reviewed_at = timezone.now()
            workflow.save()
            
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='dean_rejected',
                admin_user=request.user,
                notes=notes
            )
            
            # Send notification to HOD
            from admin_hierarchy.signals import notify_dean_rejected
            notify_dean_rejected(workflow)
            
            messages.warning(request, 'Result rejected by DEAN. HOD will be notified.')
        
        return redirect('dean_dashboard')
    
    context = {
        'workflow': workflow,
        'result': workflow.result,
        'student': workflow.result.student,
        'hod': workflow.current_hod,
    }
    
    return render(request, 'admin_hierarchy/dean_review_result.html', context)


def hod_logout(request):
    """HOD logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('hod_login')


def dean_logout(request):
    """DEAN logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('dean_login')


@require_profile('exam_officer_profile', login_url='exam_officer_login')
def exam_officer_preview_results(request):
    """
    Exam officer preview of submitted results (read-only for HOD/Faculty if they access).
    Shows results awaiting publication (status = 'dean_approved').
    """
    try:
        exam_officer = request.user.exam_officer_profile
    except:
        return redirect('exam_officer_login')

    # Get all workflows with status 'dean_approved' (ready to publish)
    workflows = ResultApprovalWorkflow.objects.filter(
        status='dean_approved'
    ).select_related('result', 'result__student', 'result__program', 'result__department', 'result__faculty').order_by('-dean_reviewed_at')

    # Optional filtering by program/department/faculty
    program_id = request.GET.get('program')
    department_id = request.GET.get('department')
    faculty_id = request.GET.get('faculty')
    year_semester = request.GET.get('year_semester')
    course = request.GET.get('course', '').strip()

    if program_id:
        workflows = workflows.filter(result__program_id=program_id)
    if department_id:
        workflows = workflows.filter(result__department_id=department_id)
    if faculty_id:
        workflows = workflows.filter(result__faculty_id=faculty_id)
    
    # Filter by academic year and semester
    if year_semester:
        try:
            year, semester = year_semester.split('-')
            workflows = workflows.filter(result__academic_year=year, result__semester=semester)
        except:
            pass
    
    # Filter by course/module/subject name
    if course:
        workflows = workflows.filter(result__subject__icontains=course)

    paginator = Paginator(workflows, 20)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    # Get distinct programs, departments, faculties for filter dropdowns
    programs = Program.objects.all().distinct()
    departments = Department.objects.all().distinct()
    faculties = Faculty.objects.all().distinct()

    context = {
        'exam_officer': exam_officer,
        'page_obj': page,
        'workflows': page.object_list,
        'programs': programs,
        'departments': departments,
        'faculties': faculties,
        'selected_program': program_id,
        'selected_department': department_id,
        'selected_faculty': faculty_id,
        'selected_year_semester': year_semester,
        'selected_course': course,
    }

    return render(request, 'admin_hierarchy/exam_officer_preview.html', context)


@require_profile('exam_officer_profile', login_url='exam_officer_login')
def exam_officer_publish_result(request, workflow_id):
    """
    Exam officer publishes a single result (marks it as published).
    Once published, the result is final and students can view their grades.
    """
    try:
        exam_officer = request.user.exam_officer_profile
    except:
        return redirect('exam_officer_login')

    workflow = get_object_or_404(ResultApprovalWorkflow, id=workflow_id, status='dean_approved')
    result = workflow.result

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        if action == 'publish':
            result.is_published = True
            result.save()

            workflow.status = 'exam_officer_published'
            workflow.exam_officer_notes = notes
            workflow.exam_officer_reviewed_at = timezone.now()
            workflow.save()

            ApprovalHistory.objects.create(
                workflow=workflow,
                action='exam_officer_published',
                admin_user=request.user,
                notes=notes
            )

            # Auto-calculate GPA and total score for the student's semester folder
            try:
                if result.folder:
                    result.folder.recalculate_all()
            except Exception as e:
                # Log but don't fail if GPA calculation has issues
                pass

            # Send notifications to students, department, and faculty
            from admin_hierarchy.signals import (
                notify_student_results_published,
                notify_department_results_published,
                notify_faculty_results_published
            )
            notify_student_results_published(workflow)
            notify_department_results_published(workflow)
            notify_faculty_results_published(workflow)

            messages.success(request, f'Result for {result.student.student_id} published successfully. Students can now view their grades.')
            return redirect('exam_officer_preview_results')

        elif action == 'return':
            # Return to DEAN for further review
            workflow.status = 'dean_approved'  # Could also create 'returned' status
            workflow.exam_officer_notes = notes
            workflow.save()

            ApprovalHistory.objects.create(
                workflow=workflow,
                action='exam_officer_returned',
                admin_user=request.user,
                notes=notes
            )

            messages.info(request, 'Result returned to DEAN for further review.')
            return redirect('exam_officer_preview_results')

    context = {
        'exam_officer': exam_officer,
        'workflow': workflow,
        'result': result,
        'student': result.student,
    }

    return render(request, 'admin_hierarchy/exam_officer_publish_result.html', context)


@require_profile('hod_profile', login_url='hod_login')
def hod_student_folders(request):
    """HOD views all student semester folders in their department, grouped by program."""
    try:
        hod = request.user.hod_profile
    except:
        return redirect('hod_login')

    # Get all semester folders for students in the HOD's department
    qs = StudentSemesterFolder.objects.filter(
        student__department=hod.department
    ).select_related('student', 'program', 'department', 'faculty').order_by('-academic_year', '-semester', 'student__student_id')

    # Search by student ID or name
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(student__student_id__icontains=q) |
            Q(student__user__first_name__icontains=q) |
            Q(student__user__last_name__icontains=q)
        )

    # Optional filter by program
    program_id = request.GET.get('program')
    if program_id:
        qs = qs.filter(program_id=program_id)

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    # Get list of programs for filter dropdown (only from their department)
    programs = Program.objects.filter(department=hod.department).distinct()
    
    # Get ALL programs, departments, and faculties for archive form
    all_programs = Program.objects.all().distinct()
    all_departments = Department.objects.all().distinct()
    all_faculties = Faculty.objects.all().distinct()

    context = {
        'hod': hod,
        'page_obj': page,
        'folders': page.object_list,
        'q': q,
        'programs': programs,
        'program_id': program_id,
        'all_programs': all_programs,
        'all_departments': all_departments,
        'all_faculties': all_faculties,
    }
    return render(request, 'admin_hierarchy/hod_student_folders.html', context)


@require_profile('hod_profile', login_url='hod_login')
def hod_folder_detail(request, folder_id):
    """HOD views a specific student semester folder and all results within it."""
    try:
        hod = request.user.hod_profile
    except:
        return redirect('hod_login')

    folder = get_object_or_404(StudentSemesterFolder, id=folder_id)

    # Permission check: folder student must be in HOD's department
    if folder.student.department != hod.department:
        messages.error(request, 'You do not have access to this folder.')
        return redirect('hod_student_folders')

    # Get all results in this folder
    results = folder.results.select_related('uploaded_by', 'student').order_by('subject')

    context = {
        'hod': hod,
        'folder': folder,
        'results': results,
    }
    return render(request, 'admin_hierarchy/hod_folder_detail.html', context)


@require_profile('dean_profile', login_url='dean_login')
def dean_student_folders(request):
    """DEAN views all student semester folders in their faculty, grouped by department."""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')

    # Get all semester folders for students in the DEAN's faculty
    qs = StudentSemesterFolder.objects.filter(
        student__faculty=dean.faculty
    ).select_related('student', 'program', 'department', 'faculty').order_by('-academic_year', '-semester', 'student__student_id')

    # Search by student ID or name
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(student__student_id__icontains=q) |
            Q(student__user__first_name__icontains=q) |
            Q(student__user__last_name__icontains=q)
        )

    # Optional filter by department
    department_id = request.GET.get('department')
    if department_id:
        qs = qs.filter(department_id=department_id)

    # Optional filter by program
    program_id = request.GET.get('program')
    if program_id:
        qs = qs.filter(program_id=program_id)

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    # Get list of departments and programs for filter dropdowns (only from their faculty)
    departments = Department.objects.filter(faculty=dean.faculty).distinct()
    programs = Program.objects.filter(department__faculty=dean.faculty).distinct()
    
    # Get ALL programs, departments, and faculties for archive form
    all_programs = Program.objects.all().distinct()
    all_departments = Department.objects.all().distinct()
    all_faculties = Faculty.objects.all().distinct()

    context = {
        'dean': dean,
        'page_obj': page,
        'folders': page.object_list,
        'q': q,
        'departments': departments,
        'programs': programs,
        'department_id': department_id,
        'program_id': program_id,
        'all_programs': all_programs,
        'all_departments': all_departments,
        'all_faculties': all_faculties,
    }
    return render(request, 'admin_hierarchy/dean_student_folders.html', context)


@require_profile('dean_profile', login_url='dean_login')
def dean_folder_detail(request, folder_id):
    """DEAN views a specific student semester folder and all results within it."""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')

    folder = get_object_or_404(StudentSemesterFolder, id=folder_id)

    # Permission check: folder student must be in DEAN's faculty
    if folder.student.faculty != dean.faculty:
        messages.error(request, 'You do not have access to this folder.')
        return redirect('dean_student_folders')

    # Get all results in this folder
    results = folder.results.select_related('uploaded_by', 'student').order_by('subject')

    context = {
        'dean': dean,
        'folder': folder,
        'results': results,
    }
    return render(request, 'admin_hierarchy/dean_folder_detail.html', context)


@login_required
def export_results_csv(request):
    """Export published results as CSV filtered by faculty/department/program/year/semester.
    Accessible to superusers, staff, Exam Officer, Dean, and HOD (scoped to their units).
    """
    user = request.user
    # Only allow explicit roles (superuser, exam officer, dean, hod). Do not rely on generic staff flag.
    allowed = user.is_superuser or hasattr(user, 'exam_officer_profile') or hasattr(user, 'dean_profile') or hasattr(user, 'hod_profile')
    if not allowed:
        messages.error(request, 'You do not have permission to export results.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    faculty_id = request.GET.get('faculty')
    department_id = request.GET.get('department')
    program_id = request.GET.get('program')
    academic_year = request.GET.get('academic_year')
    semester = request.GET.get('semester')

    qs = Result.objects.filter(is_published=True).select_related('student', 'program', 'department', 'faculty', 'uploaded_by')

    # Apply explicit filters
    if program_id:
        qs = qs.filter(program_id=program_id)
    if department_id:
        qs = qs.filter(department_id=department_id)
    if faculty_id:
        qs = qs.filter(faculty_id=faculty_id)
    if academic_year:
        qs = qs.filter(academic_year=academic_year)
    if semester:
        qs = qs.filter(semester=semester)

    # Apply role scoping
    if hasattr(user, 'hod_profile') and not user.is_superuser:
        qs = qs.filter(department=user.hod_profile.department)
    if hasattr(user, 'dean_profile') and not user.is_superuser:
        qs = qs.filter(faculty=user.dean_profile.faculty)

    # Prepare CSV
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    header = [
        'student_id', 'student_name', 'faculty', 'department', 'program',
        'academic_year', 'semester', 'subject', 'result_type', 'score', 'total_score', 'grade',
        'uploaded_by', 'uploaded_date', 'published_date'
    ]
    writer.writerow(header)

    for r in qs.order_by('student__student_id', 'subject'):
        student_name = r.student.user.get_full_name() if r.student and r.student.user else ''
        uploaded_by = ''
        if getattr(r, 'uploaded_by', None):
            try:
                uploaded_by = r.uploaded_by.user.get_full_name()
            except Exception:
                uploaded_by = str(r.uploaded_by)
        writer.writerow([
            r.student.student_id if r.student else '',
            student_name,
            r.faculty.name if r.faculty else '',
            r.department.name if r.department else '',
            r.program.name if r.program else '',
            r.academic_year,
            r.semester,
            r.subject,
            r.result_type,
            float(r.score),
            float(r.total_score),
            r.grade,
            uploaded_by,
            r.uploaded_date.isoformat() if r.uploaded_date else '',
            r.published_date.isoformat() if r.published_date else '',
        ])

    resp = HttpResponse(buffer.getvalue(), content_type='text/csv')
    filename = 'results_export'
    if academic_year:
        filename += f"_{academic_year}"
    if semester:
        filename += f"_S{semester}"
    if program_id:
        try:
            p = Program.objects.get(id=program_id)
            filename += f"_{p.code}"
        except Program.DoesNotExist:
            pass
    resp['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return resp


@login_required
@require_POST
def archive_program_results(request):
    """Archive published results for a specific program/year/semester into StudentSemesterFolder records.
    Expects POST with `program_id`, `academic_year`, `semester`.
    Only allowed for superusers/staff/Dean/HOD/ExamOfficer.
    """
    user = request.user
    # Only allow explicit roles (superuser, exam officer, dean, hod). Do not rely on generic staff flag.
    allowed = user.is_superuser or hasattr(user, 'exam_officer_profile') or hasattr(user, 'dean_profile') or hasattr(user, 'hod_profile')
    if not allowed:
        messages.error(request, 'You do not have permission to archive results.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    program_id = request.POST.get('program_id')
    academic_year = request.POST.get('academic_year')
    semester = request.POST.get('semester')

    if not program_id or not academic_year or not semester:
        messages.error(request, 'Missing required parameters for archiving.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    results_qs = Result.objects.filter(is_published=True, program_id=program_id, academic_year=academic_year, semester=semester)

    # Apply role scoping
    if hasattr(user, 'hod_profile') and not user.is_superuser:
        results_qs = results_qs.filter(department=user.hod_profile.department)
    if hasattr(user, 'dean_profile') and not user.is_superuser:
        results_qs = results_qs.filter(faculty=user.dean_profile.faculty)

    student_ids = results_qs.values_list('student_id', flat=True).distinct()

    created = 0
    for sid in student_ids:
        try:
            student = Student.objects.get(id=sid)
        except Student.DoesNotExist:
            continue

        folder, created_flag = StudentSemesterFolder.objects.get_or_create(
            student=student,
            academic_year=academic_year,
            semester=semester,
            defaults={
                'program': Program.objects.filter(id=program_id).first(),
                'department': student.department,
                'faculty': student.faculty,
            }
        )
        if created_flag:
            created += 1

        # Attach all matched results for this student to the folder
        student_results = results_qs.filter(student=student)
        for res in student_results:
            if res.folder_id != folder.id:
                res.folder = folder
                try:
                    res.save()
                except Exception:
                    pass

    messages.success(request, f'Archiving complete. Created {created} new semester folders and attached results.')
    return redirect(request.META.get('HTTP_REFERER', '/'))

