"""
Views for all 15 enhanced features
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count, Q, F
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
import json
import csv

from student.models import Student, Result, Module, Program, Assessment, StudentSemesterFolder
from student.models_enhanced import (
    GradeDistributionSnapshot,
    ClassPerformanceMetrics,
    AnalyticsReport,
    CumulativeGPA,
    Transcript,
    TranscriptRequest,
    ProgramRequirement,
    StudentProgressTracker,
    AdvisorNote,
    StudentNotification,
    ScheduledNotification,
    SavedSearch,
    AcademicProbation,
    EarlyWarningAlert,
    InterventionHistory,
    CourseOffering,
    StudentEnrollment,
    ClassAttendance,
    Assignment,
    AssignmentSubmission,
    AcademicCalendar,
    AcademicCalendarEvent,
    ParentGuardian,
    GuardianAlert,
    GradeAuditLog,
    DataValidationRule,
    DataIntegrityReport,
    ProgramCurriculum,
    StudentProgression,
    GraduationEligibility,
    CohortAnalysis,
)
from student.utilities_enhanced import (
    calculate_grade_distribution,
    calculate_class_performance_metrics,
    get_trend_analysis,
    identify_at_risk_students,
    calculate_gpa_from_grades,
    recalculate_student_cumulative_gpa,
    check_academic_probation,
    generate_student_transcript,
    sign_transcript,
    get_current_academic_year,
    get_current_semester,
)


# ==================== 1. ANALYTICS & REPORTING VIEWS ====================

@login_required
def analytics_dashboard(request):
    """Main analytics dashboard"""
    academic_year = request.GET.get('academic_year', get_current_academic_year())
    semester = request.GET.get('semester', get_current_semester())
    
    # Get grade distribution
    snapshots = GradeDistributionSnapshot.objects.filter(
        academic_year=academic_year,
        semester=semester
    )
    
    # Calculate overall statistics
    total_students = sum(s.total_students for s in snapshots)
    avg_pass_rate = snapshots.aggregate(avg=Avg('pass_rate'))['avg'] or 0
    avg_score = snapshots.aggregate(avg=Avg('average_score'))['avg'] or 0
    
    # Get at-risk students
    at_risk_students = identify_at_risk_students(academic_year, semester)
    
    # Get trend data
    trends = []
    for year in range(2022, 2025):
        trend_snapshots = GradeDistributionSnapshot.objects.filter(
            academic_year=f"{year}/{year+1}"
        )
        if trend_snapshots.exists():
            trends.append({
                'year': f"{year}/{year+1}",
                'avg_pass_rate': trend_snapshots.aggregate(avg=Avg('pass_rate'))['avg'] or 0,
            })
    
    context = {
        'academic_year': academic_year,
        'semester': semester,
        'total_students': total_students,
        'avg_pass_rate': round(avg_pass_rate, 2),
        'avg_score': round(avg_score, 2),
        'at_risk_students': at_risk_students[:10],  # Top 10
        'grade_distributions': snapshots,
        'trends': trends,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def class_performance_view(request):
    """View class performance metrics"""
    modules = Module.objects.all()
    academic_year = request.GET.get('academic_year', get_current_academic_year())
    semester = request.GET.get('semester', get_current_semester())
    
    metrics = ClassPerformanceMetrics.objects.filter(
        academic_year=academic_year,
        semester=semester
    ).order_by('-class_average')
    
    paginator = Paginator(metrics, 10)
    page_number = request.GET.get('page')
    metrics_page = paginator.get_page(page_number)
    
    context = {
        'metrics': metrics_page,
        'academic_year': academic_year,
        'semester': semester,
    }
    
    return render(request, 'analytics/class_performance.html', context)


@login_required
def generate_analytics_report(request):
    """Generate custom analytics reports"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        academic_year = request.POST.get('academic_year')
        program_id = request.POST.get('program')
        
        program = Program.objects.get(id=program_id) if program_id else None
        
        # Generate report based on type
        if report_type == 'grade_distribution':
            snapshots = GradeDistributionSnapshot.objects.filter(
                academic_year=academic_year,
                program=program
            ) if program else GradeDistributionSnapshot.objects.filter(academic_year=academic_year)
            
            data = {
                'grade_a': sum(s.grade_a_count for s in snapshots),
                'grade_b': sum(s.grade_b_count for s in snapshots),
                'grade_c': sum(s.grade_c_count for s in snapshots),
                'grade_d': sum(s.grade_d_count for s in snapshots),
                'grade_f': sum(s.grade_f_count for s in snapshots),
            }
        
        report = AnalyticsReport.objects.create(
            report_type=report_type,
            title=f"{report_type.replace('_', ' ').title()} - {academic_year}",
            academic_year=academic_year,
            program=program,
            data=data,
            generated_by=request.user,
            file_format=request.POST.get('format', 'pdf'),
        )
        
        messages.success(request, 'Report generated successfully!')
        return redirect('view_analytics_report', report_id=report.id)
    
    programs = Program.objects.all()
    context = {'programs': programs}
    return render(request, 'analytics/generate_report.html', context)


@login_required
def view_analytics_report(request, report_id):
    """View generated report"""
    report = get_object_or_404(AnalyticsReport, id=report_id)
    
    # Export if requested
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{report.id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Report', report.title])
        writer.writerow(['Generated', report.generated_at])
        writer.writerow(['Type', report.report_type])
        writer.writerow([])
        
        for key, value in report.data.items():
            writer.writerow([key, value])
        
        return response
    
    context = {'report': report}
    return render(request, 'analytics/view_report.html', context)


@login_required
def export_analytics_csv(request, report_id):
    """Export analytics data as CSV"""
    report = get_object_or_404(AnalyticsReport, id=report_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_{report.id}.csv"'
    
    writer = csv.DictWriter(response, fieldnames=['metric', 'value'])
    writer.writeheader()
    
    for key, value in report.data.items():
        writer.writerow({'metric': key, 'value': value})
    
    return response


# ==================== 2. GPA SYSTEM VIEWS ====================

@login_required
def cumulative_gpa_view(request):
    """View cumulative GPA"""
    try:
        student = request.user.student_profile
        cumulative_gpa = student.cumulative_gpa
    except (AttributeError, CumulativeGPA.DoesNotExist):
        messages.error(request, 'GPA data not available')
        return redirect('student_dashboard')
    
    # Get semester GPAs
    semester_folders = StudentSemesterFolder.objects.filter(
        student=student
    ).order_by('-academic_year', '-semester')
    
    context = {
        'cumulative_gpa': cumulative_gpa,
        'semester_folders': semester_folders,
    }
    
    return render(request, 'gpa/cumulative_gpa.html', context)


@login_required
def gpa_progress_view(request):
    """View GPA progress over time"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    semester_data = StudentSemesterFolder.objects.filter(
        student=student,
        is_gpa_calculated=True
    ).order_by('academic_year', 'semester').values_list('academic_year', 'semester', 'gpa')
    
    chart_data = [
        {
            'label': f"{year} S{sem}",
            'gpa': float(gpa),
        }
        for year, sem, gpa in semester_data
    ]
    
    context = {
        'chart_data': json.dumps(chart_data),
        'student': student,
    }
    
    return render(request, 'gpa/progress.html', context)


@login_required
def academic_standing_view(request):
    """View academic standing"""
    try:
        student = request.user.student_profile
        cumulative_gpa = student.cumulative_gpa
    except (AttributeError, CumulativeGPA.DoesNotExist):
        messages.error(request, 'Academic standing data not available')
        return redirect('student_dashboard')
    
    # Get probation status if any
    probation = AcademicProbation.objects.filter(student=student, is_active=True).first()
    
    context = {
        'student': student,
        'cumulative_gpa': cumulative_gpa,
        'probation': probation,
        'on_deans_list': cumulative_gpa.on_deans_list,
    }
    
    return render(request, 'gpa/academic_standing.html', context)


# ==================== 3. TRANSCRIPT VIEWS ====================

@login_required
def request_transcript(request):
    """Request official transcript"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        recipient = request.POST.get('recipient')
        required_by = request.POST.get('required_by_date')
        
        transcript_request = TranscriptRequest.objects.create(
            student=student,
            purpose=purpose,
            recipient=recipient,
            required_by_date=required_by,
        )
        
        messages.success(request, 'Transcript request submitted successfully!')
        return redirect('my_transcripts')
    
    return render(request, 'transcripts/request_transcript.html')


@login_required
def my_transcripts(request):
    """View my transcripts and requests"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    transcripts = Transcript.objects.filter(student=student)
    requests = TranscriptRequest.objects.filter(student=student)
    
    context = {
        'transcripts': transcripts,
        'transcript_requests': requests,
    }
    
    return render(request, 'transcripts/my_transcripts.html', context)


@login_required
def download_transcript(request, transcript_id):
    """Download transcript PDF"""
    transcript = get_object_or_404(Transcript, id=transcript_id)
    
    # Verify ownership
    if transcript.student.user != request.user:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if transcript.pdf_file:
        return redirect(transcript.pdf_file.url)
    
    messages.error(request, 'Transcript file not available')
    return redirect('my_transcripts')


@login_required
def manage_transcript_requests(request):
    """Manage transcript requests (admin/staff)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    status = request.GET.get('status', 'pending')
    
    requests = TranscriptRequest.objects.filter(status=status).select_related('student')
    
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)
    
    context = {
        'transcript_requests': requests_page,
        'current_status': status,
    }
    
    return render(request, 'transcripts/manage_requests.html', context)


# ==================== 4. ACADEMIC ADVISEMENT VIEWS ====================

@login_required
def program_requirements_view(request):
    """View program requirements"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    requirement = ProgramRequirement.objects.filter(
        program=student.program
    ).first()
    
    progress_tracker = getattr(student, 'progress_tracker', None)
    
    context = {
        'requirement': requirement,
        'progress_tracker': progress_tracker,
        'student': student,
    }
    
    return render(request, 'advisement/program_requirements.html', context)


@login_required
def graduation_checklist(request):
    """View graduation checklist"""
    try:
        student = request.user.student_profile
        eligibility = student.graduation_eligibility
    except (AttributeError, GraduationEligibility.DoesNotExist):
        messages.error(request, 'Graduation eligibility data not available')
        return redirect('student_dashboard')
    
    progress = (eligibility.credits_completed / eligibility.credits_required * 100) if eligibility.credits_required else 0
    
    context = {
        'eligibility': eligibility,
        'progress_percent': round(progress, 2),
        'is_eligible': eligibility.is_eligible,
    }
    
    return render(request, 'advisement/graduation_checklist.html', context)


@login_required
def advisor_notes_view(request):
    """View advisor notes"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    notes = AdvisorNote.objects.filter(student=student).order_by('-note_date')
    
    context = {
        'notes': notes,
    }
    
    return render(request, 'advisement/advisor_notes.html', context)


# ==================== 5. NOTIFICATIONS VIEWS ====================

@login_required
def my_notifications(request):
    """View my notifications"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    notifications = StudentNotification.objects.filter(student=student).order_by('-created_at')
    
    # Mark as read
    unread_ids = request.GET.getlist('read')
    if unread_ids:
        StudentNotification.objects.filter(id__in=unread_ids).update(
            is_read=True,
            read_date=timezone.now()
        )
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications_page,
        'unread_count': unread_count,
    }
    
    return render(request, 'notifications/my_notifications.html', context)


@login_required
def schedule_notification(request):
    """Schedule bulk notification (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        recipient_type = request.POST.get('recipient_type')
        scheduled_date = request.POST.get('scheduled_date')
        channel = request.POST.get('channel')
        
        scheduled_notif = ScheduledNotification.objects.create(
            title=title,
            message=message,
            recipient_type=recipient_type,
            scheduled_date=scheduled_date,
            channel=channel,
            created_by=request.user,
        )
        
        # Add recipients if custom
        if recipient_type == 'custom':
            student_ids = request.POST.getlist('student_ids')
            students = Student.objects.filter(id__in=student_ids)
            scheduled_notif.recipient_students.set(students)
        
        messages.success(request, 'Notification scheduled successfully!')
        return redirect('admin_dashboard')
    
    programs = Program.objects.all()
    context = {'programs': programs}
    return render(request, 'notifications/schedule.html', context)


# ==================== 6. SEARCH & FILTERING VIEWS ====================

@login_required
def advanced_search(request):
    """Advanced search and filtering"""
    query = request.GET.get('q', '')
    filter_type = request.GET.get('type', 'students')
    
    results = []
    
    if filter_type == 'students':
        results = Student.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(email__icontains=query)
        )
    
    elif filter_type == 'courses':
        results = Module.objects.filter(
            Q(code__icontains=query) |
            Q(name__icontains=query)
        )
    
    elif filter_type == 'results':
        results = Result.objects.filter(
            Q(student__student_id__icontains=query) |
            Q(subject__icontains=query)
        )
    
    paginator = Paginator(results, 20)
    page_number = request.GET.get('page')
    results_page = paginator.get_page(page_number)
    
    context = {
        'results': results_page,
        'query': query,
        'filter_type': filter_type,
    }
    
    return render(request, 'search/advanced_search.html', context)


@login_required
def saved_searches(request):
    """Manage saved searches"""
    searches = SavedSearch.objects.filter(user=request.user)
    
    if request.method == 'POST':
        search_name = request.POST.get('search_name')
        search_params = request.POST.dict()
        
        SavedSearch.objects.create(
            user=request.user,
            search_name=search_name,
            search_params={k: v for k, v in search_params.items() if k != 'search_name'},
        )
        
        messages.success(request, 'Search saved successfully!')
    
    context = {'saved_searches': searches}
    return render(request, 'search/saved_searches.html', context)


# ==================== 7. PROBATION & INTERVENTION VIEWS ====================

@login_required
def academic_probation_view(request):
    """View academic probation status"""
    try:
        student = request.user.student_profile
        probation = student.academic_probation
    except (AttributeError, AcademicProbation.DoesNotExist):
        messages.info(request, 'You are not on academic probation')
        return redirect('student_dashboard')
    
    improvement_plans = probation.improvement_plans.all()
    interventions = student.interventions.all()
    
    context = {
        'probation': probation,
        'improvement_plans': improvement_plans,
        'interventions': interventions,
    }
    
    return render(request, 'probation/probation_status.html', context)


@login_required
def early_warnings_view(request):
    """View early warning alerts"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    warnings = EarlyWarningAlert.objects.filter(student=student).order_by('-alert_date')
    
    context = {
        'warnings': warnings,
    }
    
    return render(request, 'probation/early_warnings.html', context)


# ==================== 8-15. ADDITIONAL VIEWS ====================
# Placeholder views for other features - implement similarly to above

@login_required
def course_enrollments(request):
    """View course enrollments"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    enrollments = StudentEnrollment.objects.filter(
        student=student,
        status='enrolled'
    ).select_related('course_offering__module', 'course_offering__lecturer')
    
    context = {
        'enrollments': enrollments,
    }
    
    return render(request, 'courses/my_enrollments.html', context)


@login_required
def class_attendance_view(request):
    """View class attendance"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    attendance = ClassAttendance.objects.filter(student=student).order_by('-attendance_date')
    
    # Calculate attendance percentage
    total_classes = attendance.count()
    present_count = attendance.filter(is_present=True).count()
    attendance_percent = (present_count / total_classes * 100) if total_classes > 0 else 0
    
    context = {
        'attendance_records': attendance[:50],  # Last 50
        'attendance_percent': round(attendance_percent, 2),
        'total_classes': total_classes,
        'present_count': present_count,
    }
    
    return render(request, 'courses/attendance.html', context)


@login_required
def my_assignments(request):
    """View assignments for enrolled courses"""
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Student profile not found')
        return redirect('home')
    
    enrollments = StudentEnrollment.objects.filter(student=student, status='enrolled')
    course_offerings = enrollments.values_list('course_offering_id', flat=True)
    
    assignments = Assignment.objects.filter(
        course_offering_id__in=course_offerings
    ).order_by('due_date')
    
    context = {
        'assignments': assignments,
    }
    
    return render(request, 'assignments/my_assignments.html', context)


@login_required
def parent_student_results(request):
    """Parent/Guardian view of student results"""
    try:
        guardian = ParentGuardian.objects.get(user=request.user)
        student = guardian.student
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Guardian account not found')
        return redirect('home')
    
    if not guardian.can_view_results:
        messages.error(request, 'You do not have permission to view results')
        return redirect('home')
    
    folders = StudentSemesterFolder.objects.filter(student=student).order_by('-academic_year', '-semester')
    
    context = {
        'student': student,
        'folders': folders,
        'guardian': guardian,
    }
    
    return render(request, 'parent/student_results.html', context)


@login_required
def academic_calendar_view(request):
    """View academic calendar"""
    academic_year = request.GET.get('academic_year', get_current_academic_year())
    
    try:
        calendar = AcademicCalendar.objects.get(academic_year=academic_year)
    except AcademicCalendar.DoesNotExist:
        messages.warning(request, 'Calendar not available for this year')
        return redirect('home')
    
    events = calendar.events.all().order_by('start_date')
    semesters = calendar.semesters.all()
    
    context = {
        'calendar': calendar,
        'events': events,
        'semesters': semesters,
    }
    
    return render(request, 'calendar/academic_calendar.html', context)


@login_required
def data_integrity_report(request):
    """View data integrity reports (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    reports = DataIntegrityReport.objects.all().order_by('-report_date')
    
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    reports_page = paginator.get_page(page_number)
    
    context = {
        'integrity_reports': reports_page,
    }
    
    return render(request, 'admin/data_integrity.html', context)
