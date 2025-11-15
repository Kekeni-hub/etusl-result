from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Etu_student_result.decorators import require_profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q

from .models import ExamOfficer, Notification, SystemReport
from student.models import Student, Faculty, Department, Result, Program
from student.models_enhanced import ResultPublishingNotice, StudentResultMessage, GradeSubmissionDeadlineNotice, StaffGradeNotification
from lecturer.models import Lecturer
from admin_hierarchy.models import ResultApprovalWorkflow, ApprovalHistory, HeadOfDepartment, DeanOfFaculty
from .forms import OfficerStudentForm, OfficerProgramForm


@require_http_methods(["GET", "POST"])
def admin_login(request):
    """Admin/Exam Officer login"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'exam_officer_profile'):
            return redirect('admin_dashboard')
    
    if request.method == 'POST':
        # Accept either username or email for login to improve usability.
        identifier = request.POST.get('identifier') or request.POST.get('email')
        password = request.POST.get('password')

        user = None

        # If identifier looks like an email address, try email-based lookup first
        if identifier and '@' in identifier:
            try:
                exam_officer = ExamOfficer.objects.get(email__iexact=identifier)
                user = exam_officer.user
            except ExamOfficer.DoesNotExist:
                # Fallback: try to find a User with this email
                user = User.objects.filter(email__iexact=identifier).first()
        else:
            # Try username lookup
            user = User.objects.filter(username__iexact=identifier).first()

        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                # Ensure the user has an exam_officer profile and is active
                try:
                    exam_officer = ExamOfficer.objects.get(user=user)
                    if not exam_officer.is_active:
                        messages.error(request, 'Your account has been deactivated.')
                        return redirect('admin_login')
                except ExamOfficer.DoesNotExist:
                    messages.error(request, 'Admin profile not found.')
                    return redirect('admin_login')

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome, {user.first_name}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'admin/admin_login.html')


def admin_portal(request):
    """Landing page for admin role selection (Lecturer, HOD, DEAN, Exam Officer)."""
    return render(request, 'admin/admin_portal.html')


@require_profile('exam_officer_profile', login_url='admin_login')
def admin_dashboard(request):
    """Admin dashboard with overview"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    # Get statistics
    total_students = Student.objects.filter(is_active=True).count()
    total_lecturers = Lecturer.objects.filter(is_active=True).count()
    pending_verification = Lecturer.objects.filter(is_verified=False, is_active=True).count()
    published_results = Result.objects.filter(is_published=True).count()
    pending_results = Result.objects.filter(is_published=False).count()
    
    # Get DEAN approved results waiting for THIS EXAM OFFICER's publication
    dean_approved_count = ResultApprovalWorkflow.objects.filter(
        status='dean_approved',
        current_exam_officer=admin
    ).count()
    
    # Get workflow statistics
    workflows_published = ResultApprovalWorkflow.objects.filter(
        current_exam_officer=admin,
        status='exam_published'
    ).count()
    
    context = {
        'admin': admin,
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'pending_verification': pending_verification,
        'published_results': published_results,
        'pending_results': pending_results,
        'dean_approved_count': dean_approved_count,
        'workflows_published': workflows_published,
    }
    
    return render(request, 'admin/admin_dashboard.html', context)


@login_required(login_url='admin_login')
def manage_faculties(request):
    """Manage faculties"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            code = request.POST.get('code')
            description = request.POST.get('description')
            
            if Faculty.objects.filter(code=code).exists():
                messages.error(request, 'Faculty code already exists.')
            else:
                Faculty.objects.create(name=name, code=code, description=description)
                messages.success(request, 'Faculty added successfully.')
        
        elif action == 'edit':
            faculty_id = request.POST.get('faculty_id')
            name = request.POST.get('name')
            code = request.POST.get('code')
            description = request.POST.get('description')
            
            faculty = get_object_or_404(Faculty, id=faculty_id)
            faculty.name = name
            faculty.code = code
            faculty.description = description
            faculty.save()
            messages.success(request, 'Faculty updated successfully.')
        
        elif action == 'delete':
            faculty_id = request.POST.get('faculty_id')
            faculty = get_object_or_404(Faculty, id=faculty_id)
            faculty.delete()
            messages.success(request, 'Faculty deleted successfully.')
        
        return redirect('manage_faculties')
    
    faculties = Faculty.objects.all()
    paginator = Paginator(faculties, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'faculties': page_obj.object_list,
    }
    
    return render(request, 'admin/manage_faculties.html', context)


@login_required(login_url='admin_login')
def manage_departments(request):
    """Manage departments"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            code = request.POST.get('code')
            faculty_id = request.POST.get('faculty')
            description = request.POST.get('description')
            
            faculty = get_object_or_404(Faculty, id=faculty_id)
            
            if Department.objects.filter(code=code).exists():
                messages.error(request, 'Department code already exists.')
            else:
                Department.objects.create(name=name, code=code, faculty=faculty, description=description)
                messages.success(request, 'Department added successfully.')
        
        elif action == 'edit':
            department_id = request.POST.get('department_id')
            name = request.POST.get('name')
            code = request.POST.get('code')
            faculty_id = request.POST.get('faculty')
            description = request.POST.get('description')
            
            department = get_object_or_404(Department, id=department_id)
            faculty = get_object_or_404(Faculty, id=faculty_id)
            
            department.name = name
            department.code = code
            department.faculty = faculty
            department.description = description
            department.save()
            messages.success(request, 'Department updated successfully.')
        
        elif action == 'delete':
            department_id = request.POST.get('department_id')
            department = get_object_or_404(Department, id=department_id)
            department.delete()
            messages.success(request, 'Department deleted successfully.')
        
        return redirect('manage_departments')
    
    departments = Department.objects.all().select_related('faculty')
    faculties = Faculty.objects.all()
    paginator = Paginator(departments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'departments': page_obj.object_list,
        'faculties': faculties,
    }
    
    return render(request, 'admin/manage_departments.html', context)


@login_required(login_url='admin_login')
def officer_add_student(request):
    """Admin/Exam officer can add a student (choose faculty/department/program)."""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')

    if request.method == 'POST':
        form = OfficerStudentForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            from django.utils.crypto import get_random_string
            password = get_random_string(10)
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=password
            )
            student = Student.objects.create(
                user=user,
                student_id=data['student_id'],
                email=data['email'],
                phone=data.get('phone', ''),
                faculty=data['faculty'],
                department=data['department'],
                program=data['program'],
                current_year=int(data['current_year']),
                date_of_birth=data.get('date_of_birth'),
                address=data.get('address', ''),
                is_active=True,
                photo=data.get('photo') or None
            )
            messages.success(request, f"Student {user.get_full_name()} created. Temporary password: {password}")
            return redirect('admin_dashboard')
    else:
        form = OfficerStudentForm()

    return render(request, 'admin/add_student.html', {'form': form, 'admin': request.user})


@login_required(login_url='admin_login')
def officer_add_program(request):
    """Admin/Exam officer can add a program under any department."""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')

    if request.method == 'POST':
        form = OfficerProgramForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            program = Program.objects.create(
                name=data['name'],
                code=data['code'],
                department=data['department'],
                description=data.get('description', '')
            )
            messages.success(request, f"Program '{program.name}' created.")
            return redirect('admin_dashboard')
    else:
        form = OfficerProgramForm()

    return render(request, 'admin/add_program.html', {'form': form, 'admin': request.user})


@login_required(login_url='admin_login')
def manage_results(request):
    """Manage and publish student results"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'publish':
            result_id = request.POST.get('result_id')
            result = get_object_or_404(Result, id=result_id)
            result.is_published = True
            result.published_date = timezone.now()
            result.save()
            
            # Create notification for student
            Notification.objects.create(
                title='Your result is published',
                message=f'Your {result.subject} result has been published.',
                notification_type='result',
                recipient=result.student.user,
                created_by=request.user,
            )
            messages.success(request, 'Result published successfully.')
        
        elif action == 'unpublish':
            result_id = request.POST.get('result_id')
            result = get_object_or_404(Result, id=result_id)
            result.is_published = False
            result.save()
            messages.success(request, 'Result unpublished successfully.')
        
        elif action == 'delete':
            result_id = request.POST.get('result_id')
            result = get_object_or_404(Result, id=result_id)
            result.delete()
            messages.success(request, 'Result deleted successfully.')
        
        return redirect('manage_results')
    
    # Filter options
    faculty_filter = request.GET.get('faculty')
    department_filter = request.GET.get('department')
    status_filter = request.GET.get('status', 'all')
    
    results = Result.objects.all().select_related('student', 'program', 'department', 'faculty')
    
    if faculty_filter:
        results = results.filter(faculty_id=faculty_filter)
    
    if department_filter:
        results = results.filter(department_id=department_filter)
    
    if status_filter == 'published':
        results = results.filter(is_published=True)
    elif status_filter == 'pending':
        results = results.filter(is_published=False)
    
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    paginator = Paginator(results, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'results': page_obj.object_list,
        'faculties': faculties,
        'departments': departments,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/manage_results.html', context)


@login_required(login_url='admin_login')
def send_notification(request):
    """Send notification to different recipient categories"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type', 'system')
        recipient_categories = request.POST.getlist('recipient_categories[]')
        
        recipients_list = []
        count = 0
        
        # Collect recipients based on selected categories
        if 'STUDENTS' in recipient_categories:
            student_users = User.objects.filter(student__is_active=True).distinct()
            recipients_list.extend(student_users)
            count += student_users.count()
        
        if 'LECTURERS' in recipient_categories:
            lecturer_users = User.objects.filter(lecturer__is_active=True).distinct()
            recipients_list.extend(lecturer_users)
            count += lecturer_users.count()
        
        if 'HODS' in recipient_categories:
            hod_users = User.objects.filter(headofdepartment__is_active=True).distinct()
            recipients_list.extend(hod_users)
            count += hod_users.count()
        
        if 'DEAN' in recipient_categories:
            dean_users = User.objects.filter(deanoffaculty__is_active=True).distinct()
            recipients_list.extend(dean_users)
            count += dean_users.count()
        
        # Remove duplicates
        unique_users = list(set(recipients_list))
        
        # Create notifications
        for recipient in unique_users:
            Notification.objects.create(
                title=title,
                message=message,
                notification_type=notification_type,
                recipient=recipient,
                created_by=request.user,
            )
        
        messages.success(request, f'Notification sent to {len(unique_users)} recipient(s) across {len(recipient_categories)} categories.')
        return redirect('send_notification')
    
    context = {
        'recipient_categories': [
            {'name': 'STUDENTS', 'label': 'All Students'},
            {'name': 'LECTURERS', 'label': 'All Lecturers'},
            {'name': 'HODS', 'label': 'All Heads of Department'},
            {'name': 'DEAN', 'label': 'All Deans'},
        ]
    }
    
    return render(request, 'admin/send_notification.html', context)


@login_required(login_url='admin_login')
def view_reports(request):
    """View system reports"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    reports = SystemReport.objects.all().order_by('-generated_date')
    
    # Filter options
    report_type = request.GET.get('report_type')
    faculty_filter = request.GET.get('faculty')
    
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    if faculty_filter:
        reports = reports.filter(faculty_id=faculty_filter)
    
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    faculties = Faculty.objects.all()
    report_types = [
        ('student_results', 'Student Results Report'),
        ('lecturer_upload', 'Lecturer Upload Report'),
        ('published_results', 'Published Results Report'),
        ('system', 'System Report'),
    ]
    
    context = {
        'page_obj': page_obj,
        'reports': page_obj.object_list,
        'faculties': faculties,
        'report_types': report_types,
    }
    
    return render(request, 'admin/view_reports.html', context)


def admin_logout(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')


@login_required(login_url='admin_login')
def manage_dean_approved_results(request):
    """Manage dean-approved results for publication by EXAM Officer"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    # Get all dean-approved workflows waiting for EXAM Officer
    q = request.GET.get('q', '').strip()
    workflows = ResultApprovalWorkflow.objects.filter(
        status='dean_approved',
        current_exam_officer=admin
    ).select_related('result__student', 'current_dean', 'current_hod').order_by('-dean_reviewed_at')
    
    # Search by student ID or subject
    if q:
        workflows = workflows.filter(
            Q(result__student__student_id__icontains=q) |
            Q(result__subject__icontains=q)
        )
    
    paginator = Paginator(workflows, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'workflows': page_obj.object_list,
        'q': q,
        'pending_count': ResultApprovalWorkflow.objects.filter(
            status='dean_approved',
            current_exam_officer=admin
        ).count(),
    }
    
    return render(request, 'admin/manage_dean_approved_results.html', context)


@login_required(login_url='admin_login')
def publish_result(request, workflow_id):
    """EXAM Officer publishes or rejects a dean-approved result"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    workflow = get_object_or_404(ResultApprovalWorkflow, id=workflow_id, status='dean_approved', current_exam_officer=admin)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'publish':
            # Publish the result - mark as published and update workflow status
            workflow.result.is_published = True
            workflow.result.published_date = timezone.now()
            workflow.result.save()
            
            workflow.status = 'exam_published'
            workflow.exam_reviewed_at = timezone.now()
            workflow.exam_notes = notes if notes else 'Approved and published by EXAM Officer'
            workflow.save()
            
            # Log the action in ApprovalHistory
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='exam_published',
                admin_user=request.user,
                notes=notes
            )
            
            messages.success(request, f'Result for {workflow.result.student.student_id} - {workflow.result.subject} published successfully!')
            return redirect('manage_dean_approved_results')
        
        elif action == 'reject':
            # Reject the result - send back to DEAN
            workflow.status = 'dean_rejected'  # Change back to allow DEAN to review
            workflow.exam_reviewed_at = timezone.now()
            workflow.exam_notes = notes
            workflow.save()
            
            # Log the action in ApprovalHistory
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='exam_rejected',
                admin_user=request.user,
                notes=notes
            )
            
            messages.warning(request, f'Result for {workflow.result.student.student_id} - {workflow.result.subject} rejected. Sent back to DEAN for review.')
            return redirect('manage_dean_approved_results')
    
    context = {
        'workflow': workflow,
        'result': workflow.result,
        'student': workflow.result.student,
    }
    
    return render(request, 'admin/publish_result.html', context)


# ==================== RESULT PUBLISHING NOTIFICATIONS ====================

@require_profile('exam_officer_profile', login_url='admin_login')
def create_result_publishing_notice(request):
    """Create a result publishing notice to send to all students"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    if request.method == 'POST':
        program_id = request.POST.get('program')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        publishing_date = request.POST.get('publishing_date')
        publishing_time = request.POST.get('publishing_time')
        message = request.POST.get('message')
        
        try:
            from student.models_enhanced import ResultPublishingNotice, StudentResultMessage
            from datetime import datetime
            
            program = Program.objects.get(id=program_id)
            
            # Create publishing notice
            notice = ResultPublishingNotice.objects.create(
                program=program,
                semester=semester,
                academic_year=academic_year,
                publishing_date=datetime.strptime(f"{publishing_date} {publishing_time}", "%Y-%m-%d %H:%M"),
                publishing_time=publishing_time,
                message=message,
                created_by=request.user,
                status='draft'
            )
            
            messages.success(request, 'Publishing notice created. You can now send it to students.')
            return redirect('send_result_publishing_notice', notice_id=notice.id)
        
        except Exception as e:
            messages.error(request, f'Failed to create notice: {str(e)}')
    
    programs = Program.objects.all()
    context = {
        'programs': programs,
    }
    return render(request, 'admin/create_publishing_notice.html', context)


@require_profile('exam_officer_profile', login_url='admin_login')
def send_result_publishing_notice(request, notice_id):
    """Send result publishing notice to all students"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    from student.models_enhanced import ResultPublishingNotice, StudentResultMessage
    
    notice = get_object_or_404(ResultPublishingNotice, id=notice_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send':
            # Get all students in the program
            students = Student.objects.filter(
                program=notice.program,
                is_active=True
            )
            
            publishing_datetime = notice.publishing_date
            
            # Create messages for each student
            messages_created = 0
            for student in students:
                # Message shows only publishing date/time - NOT deadline info
                if publishing_datetime:
                    try:
                        pub_date_str = publishing_datetime.strftime('%B %d, %Y')
                    except Exception:
                        pub_date_str = str(publishing_datetime)
                    try:
                        pub_time_str = publishing_datetime.strftime('%I:%M %p')
                    except Exception:
                        pub_time_str = ''
                else:
                    pub_date_str = 'TBA'
                    pub_time_str = ''

                message_body = notice.message.replace('{date}', pub_date_str)
                message_body = message_body.replace('{time}', pub_time_str)
                
                StudentResultMessage.objects.create(
                    publishing_notice=notice,
                    student=student,
                    subject=notice.title,
                    message_body=message_body,
                    publishing_date=publishing_datetime,
                    delivery_status='sent',
                    sent_via_dashboard=True,
                    sent_via_email=notice.send_email,
                    sent_at=timezone.now()
                )
                messages_created += 1
            
            # Update notice
            notice.status = 'sent'
            notice.sent_date = timezone.now()
            notice.total_recipients = students.count()
            notice.successfully_sent = messages_created
            notice.save()
            
            messages.success(request, f'Publishing notice sent to {messages_created} students.')
            return redirect('admin_dashboard')
        
        elif action == 'schedule':
            notice.status = 'scheduled'
            notice.save()
            messages.success(request, 'Notice scheduled.')
    
    context = {
        'notice': notice,
    }
    return render(request, 'admin/send_publishing_notice.html', context)


# ==================== GRADE SUBMISSION DEADLINE NOTIFICATIONS ====================

@require_profile('exam_officer_profile', login_url='admin_login')
def create_grade_deadline_notice(request):
    """Create grade submission/verification/approval deadline notices"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    if request.method == 'POST':
        program_id = request.POST.get('program')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        submission_start = request.POST.get('submission_start_date')
        submission_deadline = request.POST.get('submission_deadline')
        verification_start = request.POST.get('verification_start_date')
        verification_deadline = request.POST.get('verification_deadline')
        approval_start = request.POST.get('approval_start_date')
        approval_deadline = request.POST.get('approval_deadline')
        
        submission_message = request.POST.get('submission_message')
        verification_message = request.POST.get('verification_message')
        approval_message = request.POST.get('approval_message')
        
        try:
            from student.models_enhanced import GradeSubmissionDeadlineNotice
            from datetime import datetime
            
            program = Program.objects.get(id=program_id)
            
            notice = GradeSubmissionDeadlineNotice.objects.create(
                program=program,
                semester=semester,
                academic_year=academic_year,
                submission_start_date=datetime.fromisoformat(submission_start),
                submission_deadline=datetime.fromisoformat(submission_deadline),
                verification_start_date=datetime.fromisoformat(verification_start) if verification_start else None,
                verification_deadline=datetime.fromisoformat(verification_deadline) if verification_deadline else None,
                approval_deadline=datetime.fromisoformat(approval_deadline) if approval_deadline else None,
                submission_message=submission_message,
                verification_message=verification_message,
                approval_message=approval_message,
                created_by=request.user,
                status='draft'
            )
            
            messages.success(request, 'Grade deadline notice created.')
            return redirect('send_grade_deadline_notice', notice_id=notice.id)
        
        except Exception as e:
            messages.error(request, f'Failed to create notice: {str(e)}')
    
    programs = Program.objects.all()
    context = {
        'programs': programs,
    }
    return render(request, 'admin/create_grade_deadline_notice.html', context)


@require_profile('exam_officer_profile', login_url='admin_login')
def send_grade_deadline_notice(request, notice_id):
    """Send grade deadline notifications to lecturers, HODs, deans"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    from student.models_enhanced import GradeSubmissionDeadlineNotice, StaffGradeNotification
    from lecturer.models import Lecturer
    from admin_hierarchy.models import HeadOfDepartment, DeanOfFaculty
    
    notice = get_object_or_404(GradeSubmissionDeadlineNotice, id=notice_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send_to_lecturers':
            # Get all lecturers for the program
            lecturers = Lecturer.objects.filter(
                department__program=notice.program,
                is_active=True
            ).distinct()
            
            for lecturer in lecturers:
                StaffGradeNotification.objects.create(
                    deadline_notice=notice,
                    recipient=lecturer.user,
                    staff_role='lecturer',
                    notification_type='submission_start',
                    subject=f'Grade Submission Deadline - {notice.program.name}',
                    message_body=notice.submission_message,
                    reference_deadline=notice.submission_deadline,
                    delivery_status='sent',
                    sent_via_email=notice.send_email,
                    sent_via_dashboard=notice.send_dashboard,
                    email_sent_at=timezone.now() if notice.send_email else None
                )
            
            messages.success(request, f'Notifications sent to {lecturers.count()} lecturers.')
        
        elif action == 'send_to_hods':
            # Get all HODs
            hods = HeadOfDepartment.objects.filter(is_active=True)
            
            for hod in hods:
                StaffGradeNotification.objects.create(
                    deadline_notice=notice,
                    recipient=hod.user,
                    staff_role='hod',
                    notification_type='verification_start' if notice.verification_start_date else 'submission_start',
                    subject=f'Grade Verification & Approval - {notice.program.name}',
                    message_body=notice.verification_message or notice.submission_message,
                    reference_deadline=notice.verification_deadline or notice.submission_deadline,
                    delivery_status='sent',
                    sent_via_email=notice.send_email,
                    sent_via_dashboard=notice.send_dashboard,
                    email_sent_at=timezone.now() if notice.send_email else None
                )
            
            messages.success(request, f'Notifications sent to {hods.count()} HODs.')
        
        elif action == 'send_to_deans':
            # Get all Deans
            deans = DeanOfFaculty.objects.filter(is_active=True)
            
            for dean in deans:
                StaffGradeNotification.objects.create(
                    deadline_notice=notice,
                    recipient=dean.user,
                    staff_role='dean',
                    notification_type='approval_start' if notice.approval_deadline else 'submission_start',
                    subject=f'Grade Approval Required - {notice.program.name}',
                    message_body=notice.approval_message or notice.submission_message,
                    reference_deadline=notice.approval_deadline or notice.submission_deadline,
                    delivery_status='sent',
                    sent_via_email=notice.send_email,
                    sent_via_dashboard=notice.send_dashboard,
                    email_sent_at=timezone.now() if notice.send_email else None
                )
            
            messages.success(request, f'Notifications sent to {deans.count()} deans.')
        
        notice.status = 'active'
        notice.activated_at = timezone.now()
        notice.save()
        
        return redirect('admin_dashboard')
    
    context = {
        'notice': notice,
    }
    return render(request, 'admin/send_grade_deadline_notice.html', context)



