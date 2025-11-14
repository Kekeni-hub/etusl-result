from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Etu_student_result.decorators import require_profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone

from .models import ExamOfficer, Notification, SystemReport
from student.models import Student, Faculty, Department, Result, Program
from lecturer.models import Lecturer
from admin_hierarchy.models import ResultApprovalWorkflow, ApprovalHistory
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
    
    # Get DEAN approved results waiting for publication
    dean_approved_count = ResultApprovalWorkflow.objects.filter(
        status='dean_approved'
    ).count()
    
    context = {
        'admin': admin,
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'pending_verification': pending_verification,
        'published_results': published_results,
        'pending_results': pending_results,
        'dean_approved_count': dean_approved_count,
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
    """Send notification to students"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type', 'system')
        recipients = request.POST.getlist('recipients[]')
        
        for recipient_id in recipients:
            recipient = get_object_or_404(User, id=recipient_id)
            Notification.objects.create(
                title=title,
                message=message,
                notification_type=notification_type,
                recipient=recipient,
                created_by=request.user,
            )
        
        messages.success(request, f'Notification sent to {len(recipients)} recipient(s).')
        return redirect('send_notification')
    
    students = Student.objects.filter(is_active=True)
    context = {
        'students': students,
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
    """Manage dean-approved results for publication"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    # Get all dean-approved workflows
    workflows = ResultApprovalWorkflow.objects.filter(
        status='dean_approved'
    ).select_related('result', 'result__student', 'current_dean').order_by('-dean_approved_date')
    
    # Filter options
    faculty_filter = request.GET.get('faculty')
    department_filter = request.GET.get('department')
    
    if faculty_filter:
        workflows = workflows.filter(result__faculty_id=faculty_filter)
    
    if department_filter:
        workflows = workflows.filter(result__department_id=department_filter)
    
    paginator = Paginator(workflows, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    
    context = {
        'page_obj': page_obj,
        'workflows': page_obj.object_list,
        'faculties': faculties,
        'departments': departments,
    }
    
    return render(request, 'admin/manage_dean_approved_results.html', context)


@login_required(login_url='admin_login')
def publish_result(request, workflow_id):
    """Publish a dean-approved result"""
    try:
        admin = request.user.exam_officer_profile
    except:
        return redirect('admin_login')
    
    workflow = get_object_or_404(ResultApprovalWorkflow, id=workflow_id, status='dean_approved')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'publish':
            # Publish the result
            workflow.result.is_published = True
            workflow.result.save()
            
            workflow.status = 'exam_published'
            workflow.exam_published_date = timezone.now()
            workflow.exam_notes = notes
            workflow.save()
            
            # Log the action in ApprovalHistory
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='exam_published',
                admin_user=request.user,
                notes=notes if notes else 'Result published by EXAM Officer'
            )
            
            messages.success(request, 'Result published successfully!')
            return redirect('manage_dean_approved_results')
        
        elif action == 'reject':
            # Reject the result - send back to DEAN
            workflow.status = 'exam_rejected'
            workflow.exam_rejected_date = timezone.now()
            workflow.exam_notes = notes
            workflow.save()
            
            # Log the action in ApprovalHistory
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='exam_rejected',
                admin_user=request.user,
                notes=notes if notes else 'Result rejected by EXAM Officer'
            )
            
            messages.success(request, 'Result rejected and sent back to DEAN for review.')
            return redirect('manage_dean_approved_results')
    
    context = {
        'workflow': workflow,
        'result': workflow.result,
    }
    
    return render(request, 'admin/publish_result.html', context)


