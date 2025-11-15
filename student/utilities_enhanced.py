"""
Utility functions for analytics, reporting, notifications, and calculations
"""

from decimal import Decimal
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from student.models import Result, Assessment, Student, Module
from student.models_enhanced import (
    GradeDistributionSnapshot,
    ClassPerformanceMetrics,
    CumulativeGPA,
    AcademicProbation,
    EarlyWarningAlert,
    StudentNotification,
    NotificationTemplate,
)


# ==================== ANALYTICS UTILITIES ====================

def calculate_grade_distribution(program, academic_year, semester):
    """Calculate grade distribution for a program in a given academic year/semester"""
    results = Result.objects.filter(
        program=program,
        academic_year=academic_year,
        semester=semester,
        is_published=True
    )
    
    if not results.exists():
        return None
    
    grade_counts = {
        'A': results.filter(grade='A').count(),
        'B': results.filter(grade='B').count(),
        'C': results.filter(grade='C').count(),
        'D': results.filter(grade='D').count(),
        'F': results.filter(grade='F').count(),
    }
    
    total_students = results.count()
    average_score = results.aggregate(avg=Avg('score'))['avg'] or 0
    pass_count = results.filter(grade__in=['A', 'B', 'C', 'D']).count()
    pass_rate = (pass_count / total_students * 100) if total_students > 0 else 0
    
    snapshot, created = GradeDistributionSnapshot.objects.get_or_create(
        academic_year=academic_year,
        semester=semester,
        program=program,
        defaults={
            'grade_a_count': grade_counts['A'],
            'grade_b_count': grade_counts['B'],
            'grade_c_count': grade_counts['C'],
            'grade_d_count': grade_counts['D'],
            'grade_f_count': grade_counts['F'],
            'average_score': average_score,
            'total_students': total_students,
            'pass_rate': pass_rate,
        }
    )
    
    if not created:
        snapshot.grade_a_count = grade_counts['A']
        snapshot.grade_b_count = grade_counts['B']
        snapshot.grade_c_count = grade_counts['C']
        snapshot.grade_d_count = grade_counts['D']
        snapshot.grade_f_count = grade_counts['F']
        snapshot.average_score = average_score
        snapshot.total_students = total_students
        snapshot.pass_rate = pass_rate
        snapshot.save()
    
    return snapshot


def calculate_class_performance_metrics(module, academic_year, semester):
    """Calculate performance metrics for a specific module"""
    results = Result.objects.filter(
        subject=module.name,
        academic_year=academic_year,
        semester=semester,
        is_published=True
    )
    
    if not results.exists():
        return None
    
    scores = [float(r.score) for r in results]
    
    class_average = sum(scores) / len(scores) if scores else 0
    highest_score = max(scores) if scores else 0
    lowest_score = min(scores) if scores else 0
    
    # Calculate standard deviation
    if len(scores) > 1:
        mean = class_average
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        std_deviation = variance ** 0.5
    else:
        std_deviation = 0
    
    pass_count = results.filter(grade__in=['A', 'B', 'C', 'D']).count()
    total = results.count()
    pass_rate = (pass_count / total * 100) if total > 0 else 0
    
    metrics, created = ClassPerformanceMetrics.objects.get_or_create(
        module=module,
        academic_year=academic_year,
        semester=semester,
        defaults={
            'class_average': class_average,
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'std_deviation': std_deviation,
            'pass_rate': pass_rate,
            'total_students_enrolled': total,
            'total_students_passed': pass_count,
            'total_students_failed': total - pass_count,
        }
    )
    
    if not created:
        metrics.class_average = class_average
        metrics.highest_score = highest_score
        metrics.lowest_score = lowest_score
        metrics.std_deviation = std_deviation
        metrics.pass_rate = pass_rate
        metrics.total_students_enrolled = total
        metrics.total_students_passed = pass_count
        metrics.total_students_failed = total - pass_count
        metrics.save()
    
    return metrics


def get_trend_analysis(program, years=3):
    """Get performance trend over multiple academic years"""
    from django.db.models import Avg
    
    trends = []
    for i in range(years):
        # Get all academic years - simplified for demonstration
        year = 2024 - i
        snapshots = GradeDistributionSnapshot.objects.filter(
            program=program,
            academic_year=f"{year}/{year+1}"
        )
        
        if snapshots.exists():
            avg_pass_rate = snapshots.aggregate(avg=Avg('pass_rate'))['avg'] or 0
            avg_score = snapshots.aggregate(avg=Avg('average_score'))['avg'] or 0
            trends.append({
                'year': f"{year}/{year+1}",
                'avg_pass_rate': avg_pass_rate,
                'avg_score': avg_score,
            })
    
    return trends


def identify_at_risk_students(academic_year, semester, gpa_threshold=1.5):
    """Identify students at risk of failing or on probation"""
    from student.models import StudentSemesterFolder
    
    at_risk = []
    
    folders = StudentSemesterFolder.objects.filter(
        academic_year=academic_year,
        semester=semester,
        gpa__lte=gpa_threshold
    ).select_related('student')
    
    for folder in folders:
        at_risk.append({
            'student': folder.student,
            'gpa': folder.gpa,
            'total_score': folder.total_score,
            'risk_level': 'Critical' if folder.gpa < 1.0 else 'High',
        })
    
    return at_risk


# ==================== GPA CALCULATION UTILITIES ====================

def calculate_gpa_from_grades(grades, scale=4.0):
    """Convert letter grades to GPA points"""
    grade_to_gpa = {
        'A': 4.0,
        'B': 3.0,
        'C': 2.0,
        'D': 1.0,
        'F': 0.0,
    }
    
    if not grades:
        return 0
    
    total_gpa = sum(grade_to_gpa.get(g, 0) for g in grades)
    return round(total_gpa / len(grades), 2)


def recalculate_student_cumulative_gpa(student):
    """Recalculate a student's cumulative GPA"""
    try:
        cumulative_gpa, created = CumulativeGPA.objects.get_or_create(student=student)
        cumulative_gpa.recalculate()
        return cumulative_gpa
    except Exception as e:
        print(f"Error recalculating GPA for {student.student_id}: {e}")
        return None


# ==================== PROBATION & WARNING UTILITIES ====================

def check_academic_probation(student, gpa_threshold=1.5):
    """Check if student should be placed on academic probation"""
    cumulative_gpa = getattr(student, 'cumulative_gpa', None)
    
    if cumulative_gpa and cumulative_gpa.overall_gpa < gpa_threshold:
        probation, created = AcademicProbation.objects.get_or_create(
            student=student,
            is_active=True,
            defaults={
                'probation_start_date': timezone.now(),
                'reason': 'low_gpa',
                'minimum_required_gpa': Decimal(str(gpa_threshold)),
            }
        )
        return probation
    
    return None


def create_early_warning_alert(student, alert_type, trigger_value, threshold):
    """Create an early warning alert for a student"""
    alert, created = EarlyWarningAlert.objects.get_or_create(
        student=student,
        alert_type=alert_type,
        defaults={
            'trigger_value': trigger_value,
            'threshold': threshold,
        }
    )
    return alert


def dismiss_academic_probation(student):
    """Remove student from academic probation"""
    try:
        probation = AcademicProbation.objects.get(student=student, is_active=True)
        probation.is_active = False
        probation.dismissed_date = timezone.now()
        probation.save()
        return True
    except AcademicProbation.DoesNotExist:
        return False


# ==================== NOTIFICATION UTILITIES ====================

def send_result_notification(student, result):
    """Send notification to student when result is published"""
    try:
        template = NotificationTemplate.objects.get(template_type='result_published')
        
        message = template.body.replace('{{student_name}}', student.user.get_full_name())
        message = message.replace('{{course_name}}', result.subject)
        message = message.replace('{{score}}', str(result.score))
        message = message.replace('{{grade}}', result.grade)
        
        notification = StudentNotification.objects.create(
            student=student,
            template=template,
            subject=template.subject,
            message=message,
            channel='email',
        )
        
        # Here you would integrate actual email/SMS sending
        # send_email_async.delay(student.email, template.subject, message)
        
        notification.is_sent = True
        notification.sent_date = timezone.now()
        notification.save()
        
        return notification
    except NotificationTemplate.DoesNotExist:
        print("Result published notification template not found")
        return None


def send_bulk_notification(recipient_list, subject, message, channel='email'):
    """Send bulk notifications to multiple students"""
    notifications = []
    
    for student in recipient_list:
        notification = StudentNotification.objects.create(
            student=student,
            subject=subject,
            message=message,
            channel=channel,
            is_sent=True,
            sent_date=timezone.now(),
        )
        notifications.append(notification)
    
    return notifications


def send_probation_alert(student, probation):
    """Send probation alert notification"""
    try:
        template = NotificationTemplate.objects.get(template_type='academic_probation')
        
        message = template.body.replace('{{student_name}}', student.user.get_full_name())
        message = message.replace('{{minimum_gpa}}', str(probation.minimum_required_gpa))
        
        notification = StudentNotification.objects.create(
            student=student,
            template=template,
            subject=template.subject,
            message=message,
            channel='email',
            is_sent=True,
            sent_date=timezone.now(),
        )
        
        return notification
    except NotificationTemplate.DoesNotExist:
        return None


# ==================== TRANSCRIPT UTILITIES ====================

def generate_student_transcript(student, transcript_type='official', start_year=None, end_year=None):
    """Generate a student transcript"""
    from student.models_enhanced import Transcript
    
    transcript = Transcript.objects.create(
        student=student,
        transcript_type=transcript_type,
        start_academic_year=start_year or '2020/2021',
        end_academic_year=end_year or '2024/2025',
    )
    
    # Here you would generate PDF/document
    # pdf_file = generate_transcript_pdf(student, start_year, end_year)
    # transcript.pdf_file = pdf_file
    
    transcript.generated_date = timezone.now()
    transcript.save()
    
    return transcript


def sign_transcript(transcript, signed_by_user):
    """Digitally sign a transcript"""
    import hashlib
    
    # Generate simple digital signature (in production use proper crypto)
    signature_data = f"{transcript.student_id}{transcript.generated_date}{signed_by_user.email}"
    digital_signature = hashlib.sha256(signature_data.encode()).hexdigest()
    
    transcript.is_signed = True
    transcript.signed_by = signed_by_user
    transcript.signed_date = timezone.now()
    transcript.digital_signature = digital_signature
    transcript.save()
    
    return transcript


# ==================== PROGRESSION TRACKING UTILITIES ====================

def update_student_progression(student):
    """Update student's progression through program"""
    from student.models_enhanced import StudentProgression, RetakeCourse
    
    try:
        progression = student.progression
        
        # Calculate current semester based on enrollment date
        from datetime import datetime
        enrollment_date = datetime.strptime(progression.enrollment_academic_year.split('/')[0], '%Y')
        current_date = timezone.now()
        
        # Approximately 2 semesters per year
        months_enrolled = (current_date.year - enrollment_date.year) * 12 + (current_date.month - enrollment_date.month)
        progression.current_curriculum_semester = (months_enrolled // 6) + 1
        
        # Check if on track
        progress_tracker = getattr(student, 'progress_tracker', None)
        if progress_tracker:
            progress_tracker.update_progress()
            progression.is_on_track = True
        
        progression.save()
        return progression
    except Exception as e:
        print(f"Error updating progression for {student.student_id}: {e}")
        return None


def check_graduation_eligibility(student):
    """Check if student is eligible for graduation"""
    from student.models_enhanced import GraduationEligibility
    
    try:
        eligibility, created = GraduationEligibility.objects.get_or_create(student=student)
        
        # Check cumulative GPA
        cumulative_gpa = getattr(student, 'cumulative_gpa', None)
        if cumulative_gpa:
            eligibility.current_gpa = cumulative_gpa.overall_gpa
            eligibility.gpa_requirement_met = cumulative_gpa.overall_gpa >= eligibility.required_gpa
        
        # Check credits (simplified)
        results = Result.objects.filter(student=student, is_published=True)
        eligibility.credits_completed = results.count() * 3  # Assuming 3 credits per course
        
        # Check all requirements
        eligibility.is_eligible = eligibility.gpa_requirement_met and eligibility.credits_completed >= eligibility.credits_required
        
        eligibility.save()
        return eligibility
    except Exception as e:
        print(f"Error checking graduation eligibility for {student.student_id}: {e}")
        return None


# ==================== CALENDAR & SEMESTER UTILITIES ====================

def get_current_academic_year():
    """Get current academic year"""
    from datetime import datetime
    today = datetime.now()
    
    if today.month < 9:  # Before September
        return f"{today.year - 1}/{today.year}"
    else:
        return f"{today.year}/{today.year + 1}"


def get_current_semester():
    """Get current semester (1 or 2)"""
    from datetime import datetime
    today = datetime.now()
    
    if today.month < 6:  # January-May = Semester 1
        return '1'
    elif today.month < 9:  # June-August = Break
        return 'break'
    else:  # September-December = Semester 2
        return '2'


def is_in_holiday_period():
    """Check if current date is in holiday period"""
    from student.models_enhanced import AcademicCalendarEvent
    from datetime import datetime
    
    today = datetime.now().date()
    
    holiday = AcademicCalendarEvent.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        is_holiday=True
    ).exists()
    
    return holiday


# ==================== DATA VALIDATION UTILITIES ====================

def validate_score(score, min_val=0, max_val=100):
    """Validate score is within range"""
    try:
        score_val = float(score)
        return min_val <= score_val <= max_val
    except (ValueError, TypeError):
        return False


def validate_gpa(gpa, scale=4.0):
    """Validate GPA is within scale"""
    try:
        gpa_val = float(gpa)
        return 0 <= gpa_val <= scale
    except (ValueError, TypeError):
        return False


def detect_duplicate_grades(student, module, academic_year, semester):
    """Detect if duplicate grade entry exists"""
    count = Assessment.objects.filter(
        student=student,
        module=module,
        academic_year=academic_year,
        semester=semester
    ).count()
    
    return count > 1


def audit_grade_change(result, old_score, new_score, changed_by, reason=''):
    """Create audit log for grade changes"""
    from student.models_enhanced import GradeAuditLog
    
    audit = GradeAuditLog.objects.create(
        result=result,
        change_type='updated',
        changed_by=changed_by,
        old_score=old_score,
        new_score=new_score,
        old_grade=result.grade,
        new_grade=result.grade,  # Update after change
        reason=reason,
    )
    
    return audit
