from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Etu_student_result.decorators import require_profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from io import BytesIO
import json

from .models import Student, Result, StudentSemesterFolder
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse


def home(request):
    """Home page for login selection"""
    return render(request, 'home.html')


def developers(request):
    """Developers page showing team members"""
    return render(request, 'developers.html')


@require_http_methods(["GET", "POST"])
def student_login(request):
    """Student login view"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'student_profile'):
            return redirect('student_dashboard')
    
    if request.method == 'POST':
        # Support two login modes:
        # 1) Password-based: provide student_id and password -> authenticate against Django User
        # 2) Info-based: provide name, student_id and email -> match Student record and log the linked User in

        student_id = request.POST.get('student_id', '').strip()
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '').strip()

        # If password provided, attempt standard authentication (username is the User.username created by DEAN)
        if password:
            # try to find the user by student_id first (username might be email as created by DEAN)
            user = None
            try:
                student = Student.objects.get(student_id__iexact=student_id, is_active=True)
                user = student.user
            except Student.DoesNotExist:
                # fallback: try to authenticate by username/email directly
                pass

            if user:
                user_auth = authenticate(request, username=user.username, password=password)
                if user_auth is not None:
                        login(request, user_auth)
                        # after login, check if student must change password
                        try:
                            student = user_auth.student_profile
                            if getattr(student, 'must_change_password', False):
                                return redirect('student_force_password_change')
                        except Exception:
                            pass
                        messages.success(request, f'Welcome back, {user_auth.first_name}!')
                        return redirect('student_dashboard')
                else:
                    messages.error(request, 'Invalid password. Please check and try again.')
            else:
                messages.error(request, 'Student account not found for provided Student ID.')
        else:
            # Info-based lookup (no password) - keep supporting the existing flow but make it more flexible
            try:
                # Try strict match first (student_id + email + name)
                student = Student.objects.get(
                    student_id__iexact=student_id,
                    email__iexact=email,
                    user__first_name__icontains=name,
                    is_active=True
                )
            except Student.DoesNotExist:
                # Fallbacks: match by student_id alone if unique and active
                students_by_id = Student.objects.filter(student_id__iexact=student_id, is_active=True)
                if students_by_id.count() == 1:
                    student = students_by_id.first()
                else:
                    student = None
            except Student.MultipleObjectsReturned:
                student = None

            if student:
                # Log the student in without password (trusted info-based login)
                login(request, student.user, backend='django.contrib.auth.backends.ModelBackend')
                # prompt to change password if required
                if getattr(student, 'must_change_password', False):
                    return redirect('student_force_password_change')
                messages.success(request, f'Welcome back, {student.user.first_name}!')
                return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid student credentials. Please check your details or try using the temporary password provided by the DEAN.')
    
    return render(request, 'student/student_login.html')


@require_profile('student_profile', login_url='student_login')
def student_dashboard(request):
    """Student dashboard"""
    try:
        student = request.user.student_profile
    except:
        return redirect('student_login')
    
    # Get all results for the student
    results = Result.objects.filter(student=student, is_published=True).order_by('-published_date')
    
    # Group results by academic year
    results_by_year = {}
    for result in results:
        year = result.academic_year
        if year not in results_by_year:
            results_by_year[year] = []
        results_by_year[year].append(result)
    
    # Get result publishing messages for this student (only publishing date/time shown)
    from .models_enhanced import StudentResultMessage
    publishing_messages = StudentResultMessage.objects.filter(
        student=student
    ).order_by('-created_at')[:5]  # Show latest 5 messages
    
    context = {
        'student': student,
        'results_by_year': results_by_year,
        'total_results': results.count(),
        'publishing_messages': publishing_messages,  # Messages about when results will be published
    }
    
    return render(request, 'student/student_dashboard.html', context)


@login_required(login_url='student_login')
def student_results_folder(request):
    """Student results folder - show all modules taken organized by semester/year with GPA"""
    try:
        student = request.user.student_profile
    except:
        return redirect('student_login')
    
    # Get all semester folders for the student
    folders = StudentSemesterFolder.objects.filter(
        student=student
    ).select_related('program', 'department', 'faculty').order_by('-academic_year', '-semester')
    
    # Get data for each folder
    folders_data = []
    for folder in folders:
        results = folder.results.filter(is_published=True).order_by('subject')
        folders_data.append({
            'folder': folder,
            'results': results,
            'total_score': folder.total_score,
            'gpa': folder.gpa,
        })
    
    # Calculate cumulative statistics (across all semesters)
    all_results = Result.objects.filter(student=student, is_published=True)
    total_modules = all_results.count()
    
    # Overall average
    avg_grade = 'N/A'
    if all_results.exists():
        grades = []
        for result in all_results:
            if result.score and result.total_score and result.total_score > 0:
                percentage = (result.score / result.total_score) * 100
                grades.append(percentage)
        if grades:
            avg_grade = f"{sum(grades) / len(grades):.2f}%"
    
    # Overall GPA (average of all semester GPAs)
    overall_gpa = 'N/A'
    if folders.exists():
        gpa_values = [f.gpa for f in folders if f.gpa > 0]
        if gpa_values:
            overall_gpa = round(sum(gpa_values) / len(gpa_values), 2)

    context = {
        'student': student,
        'folders_data': folders_data,
        'total_modules': total_modules,
        'avg_grade': avg_grade,
        'overall_gpa': overall_gpa,
    }
    
    return render(request, 'student/results_folder.html', context)


@login_required(login_url='student_login')
def download_result_pdf(request, result_id):
    """Download result as text/html (simplified without reportlab)"""
    try:
        student = request.user.student_profile
        result = Result.objects.get(id=result_id, student=student, is_published=True)
    except (Result.DoesNotExist, Student.DoesNotExist):
        messages.error(request, 'Result not found.')
        return redirect('student_dashboard')
    
    # Prepare display-safe published date
    if result.published_date:
        try:
            published_date_display = result.published_date.strftime('%d %B %Y %H:%M:%S')
        except Exception:
            published_date_display = str(result.published_date)
    else:
        published_date_display = 'N/A'

    # Create HTML content for download
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; color: #1a5490; margin-bottom: 30px; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            .info-table td {{ padding: 8px; border: 1px solid #ddd; }}
            .info-table td:first-child {{ background-color: #e8f4f8; font-weight: bold; width: 200px; }}
            .result-table {{ width: 100%; border-collapse: collapse; }}
            .result-table th {{ background-color: #1a5490; color: white; padding: 10px; text-align: left; }}
            .result-table td {{ padding: 10px; border: 1px solid #ddd; }}
            .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>STUDENT RESULT</h1>
        </div>
        
        <table class="info-table">
            <tr>
                <td>Student Name</td>
                <td>{student.user.get_full_name()}</td>
            </tr>
            <tr>
                <td>Student ID</td>
                <td>{student.student_id}</td>
            </tr>
            <tr>
                <td>Email</td>
                <td>{student.email}</td>
            </tr>
            <tr>
                <td>Faculty</td>
                <td>{student.faculty.name if student.faculty else 'N/A'}</td>
            </tr>
            <tr>
                <td>Department</td>
                <td>{student.department.name if student.department else 'N/A'}</td>
            </tr>
            <tr>
                <td>Program</td>
                <td>{student.program.name if student.program else 'N/A'}</td>
            </tr>
            <tr>
                <td>Academic Year</td>
                <td>{result.academic_year}</td>
            </tr>
            <tr>
                <td>Semester</td>
                <td>{result.get_semester_display()}</td>
            </tr>
        </table>

        <h3>Result Details</h3>
        <table class="result-table">
            <tr>
                <th>Subject</th>
                <th>Type</th>
                <th>Score</th>
                <th>Total Score</th>
                <th>Grade</th>
            </tr>
            <tr>
                <td>{result.subject}</td>
                <td>{result.get_result_type_display()}</td>
                <td>{result.score}</td>
                <td>{result.total_score}</td>
                <td>{result.grade or 'N/A'}</td>
            </tr>
        </table>

            <div class="footer">
                <p>Generated on: {published_date_display}</p>
            <p>This is an official academic record.</p>
        </div>
    </body>
    </html>
    """
    
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="result_{result.id}.html"'
    
    return response



def student_logout(request):
    """Student logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('student_login')


@require_profile('student_profile', login_url='student_login')
def student_force_password_change(request):
    """Force student to set a new password on first login."""
    try:
        student = request.user.student_profile
    except Exception:
        return redirect('student_login')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        if not new_password or not confirm_password:
            messages.error(request, 'Please enter and confirm the new password.')
            return redirect('student_force_password_change')
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('student_force_password_change')

        # set the new password
        user = request.user
        user.set_password(new_password)
        user.save()

        # clear flag
        student.must_change_password = False
        student.save()

        # keep the user logged in after password change
        update_session_auth_hash(request, user)
        messages.success(request, 'Password updated successfully.')
        return redirect('student_dashboard')

    return render(request, 'student/force_password_change.html', {'student': student})

