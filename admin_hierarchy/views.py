from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Etu_student_result.decorators import require_profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator

from .models import HeadOfDepartment, DeanOfFaculty, ResultApprovalWorkflow, ApprovalHistory
from student.models import Student, Result, Department, Faculty, Program
from .forms import DeanStudentForm
from .forms import DeanProgramForm


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
    pending_workflows = ResultApprovalWorkflow.objects.filter(
        current_dean=dean,
        status='hod_approved'
        ).select_related('result__student', 'current_hod')
    
    # Get DEAN-approved but not yet sent to EXAM
    approved_by_dean = ResultApprovalWorkflow.objects.filter(
        current_dean=dean,
        status='dean_approved'
        ).select_related('result__student')
    
    context = {
        'dean': dean,
        'pending_count': pending_workflows.count(),
        'approved_count': approved_by_dean.count(),
        'pending_workflows': pending_workflows[:10],
        'approved_workflows': approved_by_dean[:10],
    }
    
    return render(request, 'admin_hierarchy/dean_dashboard.html', context)


@login_required(login_url='dean_login')
def dean_add_student(request):
    """Allow DEAN to add a student to their faculty; departments/programs limited to dean's faculty."""
    try:
        dean = request.user.dean_profile
    except:
        return redirect('dean_login')

    if request.method == 'POST':
        form = DeanStudentForm(dean.faculty, request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            # Create the User
            from django.contrib.auth.models import User
            from django.utils.crypto import get_random_string
            # UserManager in this project doesn't expose make_random_password;
            # use Django's get_random_string to generate a temporary password.
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
                photo=data.get('photo') or None
            )

            messages.success(request, f"Student {user.get_full_name()} ({student.student_id}) created successfully. Temporary password: {password}")
            return redirect('dean_dashboard')
    else:
        form = DeanStudentForm(dean.faculty)

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
            # Ready for EXAM to publish
            workflow.save()
            
            ApprovalHistory.objects.create(
                workflow=workflow,
                action='dean_approved',
                admin_user=request.user,
                notes=notes
            )
            
            messages.success(request, 'Result approved by DEAN. Ready for EXAM officer to publish.')
        
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
