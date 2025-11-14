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

from .models import Student, Result

def home(request):
    """Home page for login selection"""
    return render(request, 'home.html')


@require_http_methods(["GET", "POST"])
def student_login(request):
    """Student login view"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'student_profile'):
            return redirect('student_dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        student_id = request.POST.get('student_id')
        email = request.POST.get('email')
        
        try:
            student = Student.objects.get(
                student_id=student_id,
                email=email,
                user__first_name__icontains=name,
                is_active=True
            )
            
            # Log the student in
            login(request, student.user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {student.user.first_name}!')
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid student credentials. Please check your details.')
        except Student.MultipleObjectsReturned:
            messages.error(request, 'Multiple students found. Please check your details.')
    
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
    
    context = {
        'student': student,
        'results_by_year': results_by_year,
        'total_results': results.count(),
    }
    
    return render(request, 'student/student_dashboard.html', context)


@login_required(login_url='student_login')
def download_result_pdf(request, result_id):
    """Download result as text/html (simplified without reportlab)"""
    try:
        student = request.user.student_profile
        result = Result.objects.get(id=result_id, student=student, is_published=True)
    except (Result.DoesNotExist, Student.DoesNotExist):
        messages.error(request, 'Result not found.')
        return redirect('student_dashboard')
    
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
            <p>Generated on: {result.published_date.strftime('%d %B %Y %H:%M:%S')}</p>
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

