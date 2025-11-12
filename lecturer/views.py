from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from datetime import datetime

from .models import Lecturer
from student.models import Student, Result, Faculty, Department, Program


def lecturer_home(request):
    """Lecturer home page"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'lecturer_profile'):
            return redirect('lecturer_dashboard')
    return render(request, 'lecturer/lecturer_home.html')


@require_http_methods(["GET", "POST"])
def lecturer_register(request):
    """Lecturer registration"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'lecturer_profile'):
            return redirect('lecturer_dashboard')
    
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        lecturer_id = request.POST.get('lecturer_id')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone = request.POST.get('phone')
        faculty_id = request.POST.get('faculty')
        department_id = request.POST.get('department')
        specialization = request.POST.get('specialization')
        
        # Validate passwords
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('lecturer_register')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('lecturer_register')
        
        # Check if lecturer ID already exists
        if Lecturer.objects.filter(lecturer_id=lecturer_id).exists():
            messages.error(request, 'Lecturer ID already registered.')
            return redirect('lecturer_register')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create lecturer profile
            faculty = Faculty.objects.get(id=faculty_id) if faculty_id else None
            department = Department.objects.get(id=department_id) if department_id else None
            
            lecturer = Lecturer.objects.create(
                user=user,
                lecturer_id=lecturer_id,
                email=email,
                phone=phone,
                faculty=faculty,
                department=department,
                specialization=specialization,
                is_verified=False
            )
            
            messages.success(request, 'Registration successful! Please wait for admin verification.')
            return redirect('lecturer_login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('lecturer_register')
    
    context = {
        'faculties': faculties,
        'departments': departments,
    }
    return render(request, 'lecturer/lecturer_register.html', context)


@require_http_methods(["GET", "POST"])
def lecturer_login(request):
    """Lecturer login"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'lecturer_profile'):
            return redirect('lecturer_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                lecturer = Lecturer.objects.get(user=user)
                
                if not lecturer.is_active:
                    messages.error(request, 'Your account has been deactivated.')
                    return redirect('lecturer_login')
                
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome, {user.first_name}!')
                return redirect('lecturer_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
        except Lecturer.DoesNotExist:
            messages.error(request, 'Lecturer profile not found.')
    
    return render(request, 'lecturer/lecturer_login.html')


@login_required(login_url='lecturer_login')
def lecturer_dashboard(request):
    """Lecturer dashboard"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    # Get statistics
    total_uploads = Result.objects.filter(uploaded_by=lecturer).count()
    pending_uploads = Result.objects.filter(uploaded_by=lecturer, is_published=False).count()
    published_uploads = Result.objects.filter(uploaded_by=lecturer, is_published=True).count()
    
    # Recent uploads
    recent_uploads = Result.objects.filter(uploaded_by=lecturer).order_by('-uploaded_date')[:10]
    
    context = {
        'lecturer': lecturer,
        'total_uploads': total_uploads,
        'pending_uploads': pending_uploads,
        'published_uploads': published_uploads,
        'recent_uploads': recent_uploads,
    }
    
    return render(request, 'lecturer/lecturer_dashboard.html', context)


@login_required(login_url='lecturer_login')
def upload_results(request):
    """Upload student results"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    if request.method == 'POST':
        students = request.POST.getlist('students[]')
        program_id = request.POST.get('program')
        subject = request.POST.get('subject')
        result_type = request.POST.get('result_type')
        scores = request.POST.getlist('scores[]')
        total_score = request.POST.get('total_score', 100)
        academic_year = request.POST.get('academic_year')
        semester = request.POST.get('semester')
        
        try:
            program = Program.objects.get(id=program_id)
            
            for i, student_id in enumerate(students):
                student = Student.objects.get(id=student_id)
                score = float(scores[i]) if i < len(scores) else 0
                
                # Calculate grade
                percentage = (score / float(total_score)) * 100
                if percentage >= 80:
                    grade = 'A'
                elif percentage >= 70:
                    grade = 'B'
                elif percentage >= 60:
                    grade = 'C'
                elif percentage >= 50:
                    grade = 'D'
                else:
                    grade = 'F'
                
                Result.objects.update_or_create(
                    student=student,
                    subject=subject,
                    result_type=result_type,
                    academic_year=academic_year,
                    semester=semester,
                    defaults={
                        'program': program,
                        'department': student.department,
                        'faculty': student.faculty,
                        'score': score,
                        'total_score': total_score,
                        'grade': grade,
                        'uploaded_by': lecturer,
                    }
                )
            
            messages.success(request, f'Successfully uploaded results for {len(students)} students.')
            return redirect('lecturer_dashboard')
        except Exception as e:
            messages.error(request, f'Upload failed: {str(e)}')
    
    # Get programs and students for the lecturer's department
    programs = Program.objects.filter(
        department__faculty=lecturer.faculty
    ) if lecturer.faculty else Program.objects.none()
    
    context = {
        'programs': programs,
        'result_types': [('exam', 'Exam'), ('test', 'Test'), ('assignment', 'Assignment'), 
                         ('presentation', 'Presentation'), ('attendance', 'Attendance')],
        'current_year': datetime.now().year,
    }
    
    return render(request, 'lecturer/upload_results.html', context)


def lecturer_logout(request):
    """Lecturer logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('lecturer_home')

