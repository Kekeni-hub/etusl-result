"""
Enhanced Models for Advanced Features:
- Analytics & Reporting Dashboard
- Advanced Grade Calculation & GPA System
- Transcript Generation & Management
- Student Academic Advisement System
- SMS/Email Notifications
- Advanced Search & Filtering
- Academic Probation & Performance Tracking
- Course/Module Management
- Workload Management for Lecturers
- Academic Calendar Management
- Parent/Guardian Portal
- Quality Assurance & Data Integrity
- API Enhancement
- Curriculum Management
- Student Progression Tracking
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from student.models import Student, Faculty, Department, Program, Module, Assessment, Result
import json


# ==================== 1. ANALYTICS & REPORTING ====================

class GradeDistributionSnapshot(models.Model):
    """Store grade distribution for analytics dashboard"""
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='grade_distributions')
    
    # Grade counts
    grade_a_count = models.IntegerField(default=0)
    grade_b_count = models.IntegerField(default=0)
    grade_c_count = models.IntegerField(default=0)
    grade_d_count = models.IntegerField(default=0)
    grade_f_count = models.IntegerField(default=0)
    
    # Averages
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    total_students = models.IntegerField(default=0)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('academic_year', 'semester', 'program')
    
    def __str__(self):
        return f"{self.program.name} - {self.academic_year} S{self.semester}"


class ClassPerformanceMetrics(models.Model):
    """Per-module/course performance metrics"""
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='performance_metrics')
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10)
    
    class_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    highest_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lowest_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    std_deviation = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    total_students_enrolled = models.IntegerField(default=0)
    total_students_passed = models.IntegerField(default=0)
    total_students_failed = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.module.code} - {self.academic_year} S{self.semester}"


class AnalyticsReport(models.Model):
    """Generated analytics reports for export"""
    REPORT_TYPE_CHOICES = [
        ('grade_distribution', 'Grade Distribution'),
        ('performance_trend', 'Performance Trend'),
        ('risk_analysis', 'Risk Analysis'),
        ('department_summary', 'Department Summary'),
        ('program_comparison', 'Program Comparison'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Report data stored as JSON for flexibility
    data = models.JSONField(default=dict, blank=True)
    
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Export options
    file_format = models.CharField(max_length=10, choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV')], default='pdf')
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} ({self.academic_year})"


# ==================== 2. ADVANCED GPA SYSTEM ====================

class GradingScale(models.Model):
    """Configurable grading scale for different institutions/programs"""
    SCALE_TYPE_CHOICES = [
        ('4.0', '4.0 Scale (US)'),
        ('5.0', '5.0 Scale (European)'),
        ('percentage', 'Percentage (0-100)'),
        ('custom', 'Custom Scale'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    scale_type = models.CharField(max_length=20, choices=SCALE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Grade mapping as JSON: {"A": {"min": 80, "max": 100, "gpa_point": 4.0}, ...}
    grade_mapping = models.JSONField(default=dict)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class CumulativeGPA(models.Model):
    """Cumulative GPA tracking across multiple semesters"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='cumulative_gpa')
    grading_scale = models.ForeignKey(GradingScale, on_delete=models.SET_NULL, null=True)
    
    overall_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_credits = models.IntegerField(default=0)
    total_credit_points = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Academic standing
    STANDING_CHOICES = [
        ('excellent', 'Excellent Standing (3.5+)'),
        ('good', 'Good Standing (3.0-3.49)'),
        ('satisfactory', 'Satisfactory Standing (2.0-2.99)'),
        ('probation', 'Academic Probation (1.0-1.99)'),
        ('poor', 'Poor Standing (<1.0)'),
    ]
    academic_standing = models.CharField(max_length=20, choices=STANDING_CHOICES, default='good')
    
    # Dean's list tracking
    on_deans_list = models.BooleanField(default=False)
    deans_list_semesters = models.JSONField(default=list)  # List of semesters where on dean's list
    
    last_recalculated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.student_id} - GPA: {self.overall_gpa}"
    
    def recalculate(self):
        """Recalculate cumulative GPA from all semester GPAs"""
        from student.models import StudentSemesterFolder
        
        folders = StudentSemesterFolder.objects.filter(student=self.student).order_by('academic_year', 'semester')
        
        if not folders.exists():
            self.overall_gpa = 0
            self.total_credits = 0
            self.total_credit_points = 0
            self.save()
            return
        
        total_gpa = 0
        count = 0
        for folder in folders:
            if folder.is_gpa_calculated:
                total_gpa += float(folder.gpa)
                count += 1
        
        if count > 0:
            self.overall_gpa = round(total_gpa / count, 2)
        
        # Update academic standing
        self._update_standing()
        self.save()
    
    def _update_standing(self):
        """Update academic standing based on GPA"""
        if self.overall_gpa >= 3.5:
            self.academic_standing = 'excellent'
            self.on_deans_list = True
        elif self.overall_gpa >= 3.0:
            self.academic_standing = 'good'
        elif self.overall_gpa >= 2.0:
            self.academic_standing = 'satisfactory'
        elif self.overall_gpa >= 1.0:
            self.academic_standing = 'probation'
        else:
            self.academic_standing = 'poor'


# ==================== 3. TRANSCRIPT GENERATION ====================

class Transcript(models.Model):
    """Student transcript records"""
    TRANSCRIPT_TYPE_CHOICES = [
        ('official', 'Official Transcript'),
        ('informal', 'Informal Transcript'),
        ('digital', 'Digital Transcript'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transcripts')
    transcript_type = models.CharField(max_length=20, choices=TRANSCRIPT_TYPE_CHOICES)
    
    # Transcript scope
    include_courses = models.BooleanField(default=True)
    include_gpa = models.BooleanField(default=True)
    include_dates = models.BooleanField(default=True)
    start_academic_year = models.CharField(max_length=20, blank=True)
    end_academic_year = models.CharField(max_length=20, blank=True)
    
    # Generated document
    pdf_file = models.FileField(upload_to='transcripts/', blank=True, null=True)
    
    # Digital signature
    is_signed = models.BooleanField(default=False)
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_transcripts')
    signed_date = models.DateTimeField(blank=True, null=True)
    digital_signature = models.CharField(max_length=500, blank=True)
    
    requested_date = models.DateTimeField(auto_now_add=True)
    generated_date = models.DateTimeField(blank=True, null=True)
    
    # Tracking
    request_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    number_of_copies = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-requested_date']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.transcript_type}"


class TranscriptRequest(models.Model):
    """Track transcript requests from students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transcript_requests')
    purpose = models.CharField(max_length=200, blank=True)
    recipient = models.CharField(max_length=200, blank=True)
    
    request_date = models.DateTimeField(auto_now_add=True)
    required_by_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('processing', 'Processing'), ('ready', 'Ready'), ('collected', 'Collected')],
        default='pending'
    )
    
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.purpose}"


# ==================== 4. ACADEMIC ADVISEMENT ====================

class ProgramRequirement(models.Model):
    """Track requirements for each program"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='requirements')
    
    total_credits_required = models.IntegerField()
    minimum_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=2.0)
    
    required_courses = models.ManyToManyField(Module, related_name='required_in_programs', blank=True)
    elective_courses = models.ManyToManyField(Module, related_name='elective_in_programs', blank=True)
    
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.program.name} Requirements"


class CoursePrerequisite(models.Model):
    """Define prerequisites for courses"""
    course = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='prerequisites')
    prerequisite_course = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='is_prerequisite_for')
    
    minimum_grade = models.CharField(max_length=5, default='D')  # Minimum grade required in prerequisite
    minimum_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Minimum percentage
    
    class Meta:
        unique_together = ('course', 'prerequisite_course')
    
    def __str__(self):
        return f"{self.course.code} requires {self.prerequisite_course.code}"


class StudentProgressTracker(models.Model):
    """Track student progress toward degree completion"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='progress_tracker')
    program_requirement = models.ForeignKey(ProgramRequirement, on_delete=models.SET_NULL, null=True)
    
    completed_credits = models.IntegerField(default=0)
    credits_progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    completed_courses = models.ManyToManyField(Module, related_name='students_completed', blank=True)
    remaining_courses = models.ManyToManyField(Module, related_name='students_remaining', blank=True)
    
    expected_graduation_year = models.IntegerField(blank=True, null=True)
    is_eligible_for_graduation = models.BooleanField(default=False)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.student_id} Progress"
    
    def update_progress(self):
        """Recalculate progress based on completed courses"""
        # This will be implemented in views/signals
        pass


class AdvisorNote(models.Model):
    """HOD/Advisor notes on student academic journey"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='advisor_notes')
    advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    note_date = models.DateTimeField(auto_now_add=True)
    note_type = models.CharField(
        max_length=20,
        choices=[('general', 'General'), ('warning', 'Warning'), ('commendation', 'Commendation'), ('intervention', 'Intervention')],
        default='general'
    )
    content = models.TextField()
    
    class Meta:
        ordering = ['-note_date']
    
    def __str__(self):
        return f"Note for {self.student.student_id} - {self.note_date.date()}"


# ==================== 5. NOTIFICATIONS SYSTEM ====================

class NotificationTemplate(models.Model):
    """Email/SMS notification templates"""
    TEMPLATE_TYPE_CHOICES = [
        ('result_published', 'Result Published'),
        ('result_pending', 'Result Pending Approval'),
        ('grade_warning', 'Grade Warning'),
        ('assignment_deadline', 'Assignment Deadline'),
        ('exam_scheduled', 'Exam Scheduled'),
        ('academic_probation', 'Academic Probation Notice'),
        ('graduation_eligible', 'Graduation Eligible'),
    ]
    
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPE_CHOICES, unique=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    
    # Template variables (JSON list of variables like {{student_name}}, {{course_name}})
    variables = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.template_type


class StudentNotification(models.Model):
    """Student notifications (email/SMS)"""
    NOTIFICATION_CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Both Email & SMS'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    channel = models.CharField(max_length=20, choices=NOTIFICATION_CHANNEL_CHOICES, default='email')
    
    is_sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification to {self.student.student_id}"


class ScheduledNotification(models.Model):
    """Scheduled bulk notifications"""
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Recipients can be all students, specific program, or specific students
    recipient_type = models.CharField(
        max_length=20,
        choices=[('all', 'All Students'), ('program', 'Program'), ('custom', 'Custom List')],
        default='all'
    )
    recipient_program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_students = models.ManyToManyField(Student, blank=True)
    
    channel = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')],
        default='email'
    )
    
    scheduled_date = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return self.title


# ==================== 6. ADVANCED SEARCH & FILTERING ====================

class SavedSearch(models.Model):
    """Allow users to save frequently used search/filter queries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    
    search_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Search parameters stored as JSON
    search_params = models.JSONField(default=dict)
    
    is_public = models.BooleanField(default=False)  # Share with other users
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-last_used', '-created_at']
    
    def __str__(self):
        return self.search_name


# ==================== 7. ACADEMIC PROBATION TRACKING ====================

class AcademicProbation(models.Model):
    """Track students on academic probation"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='academic_probation')
    
    probation_start_date = models.DateTimeField()
    probation_end_date = models.DateTimeField(blank=True, null=True)
    
    REASON_CHOICES = [
        ('low_gpa', 'Low GPA'),
        ('failing_courses', 'Failing Courses'),
        ('attendance', 'Poor Attendance'),
        ('other', 'Other'),
    ]
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    
    minimum_required_gpa = models.DecimalField(max_digits=3, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    dismissed_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Academic Probations'
    
    def __str__(self):
        return f"{self.student.student_id} - Probation"


class PerformanceImprovementPlan(models.Model):
    """PIP for struggling students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='improvement_plans')
    probation = models.ForeignKey(AcademicProbation, on_delete=models.CASCADE, related_name='improvement_plans')
    
    plan_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    objectives = models.TextField()  # What student needs to achieve
    actions = models.TextField()  # Actions student should take
    support_provided = models.TextField()  # Support institution will provide
    
    review_date = models.DateField()
    
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('completed', 'Completed'), ('unsuccessful', 'Unsuccessful')],
        default='active'
    )
    
    class Meta:
        ordering = ['-plan_date']
    
    def __str__(self):
        return f"PIP for {self.student.student_id}"


class EarlyWarningAlert(models.Model):
    """System-generated alerts for at-risk students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='early_warnings')
    
    alert_type = models.CharField(
        max_length=20,
        choices=[('low_score', 'Low Score'), ('failing', 'Failing'), ('low_attendance', 'Low Attendance')],
    )
    
    trigger_value = models.DecimalField(max_digits=5, decimal_places=2)  # Score, GPA, or attendance percentage
    threshold = models.DecimalField(max_digits=5, decimal_places=2)  # Alert threshold
    
    related_module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True)
    
    alert_date = models.DateTimeField(auto_now_add=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-alert_date']
    
    def __str__(self):
        return f"Alert for {self.student.student_id} - {self.alert_type}"


class InterventionHistory(models.Model):
    """Track all interventions made for struggling students"""
    student = models.ForeignKey(Student, on_cascade=models.CASCADE, related_name='interventions')
    
    intervention_date = models.DateTimeField(auto_now_add=True)
    intervention_type = models.CharField(
        max_length=30,
        choices=[
            ('tutoring', 'Tutoring Session'),
            ('counseling', 'Academic Counseling'),
            ('meeting', 'Advisor Meeting'),
            ('workshop', 'Study Skills Workshop'),
            ('support', 'Academic Support'),
        ]
    )
    
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    outcome = models.TextField(blank=True)
    
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-intervention_date']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.intervention_type}"


# ==================== 8. ENHANCED COURSE/MODULE MANAGEMENT ====================

class CourseOffering(models.Model):
    """Track which lecturers teach which modules in which periods"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='offerings')
    lecturer = models.ForeignKey('lecturer.Lecturer', on_delete=models.CASCADE, related_name='course_offerings')
    
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10)
    
    max_students = models.IntegerField(default=100)
    enrolled_students = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    class_location = models.CharField(max_length=100, blank=True)
    class_days = models.CharField(max_length=100, blank=True)  # MWF, TR, etc.
    class_time = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('module', 'lecturer', 'academic_year', 'semester')
    
    def __str__(self):
        return f"{self.module.code} - {self.lecturer.user.get_full_name()}"


class StudentEnrollment(models.Model):
    """Track student enrollment in courses"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='student_enrollments')
    
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('enrolled', 'Enrolled'), ('dropped', 'Dropped'), ('completed', 'Completed')],
        default='enrolled'
    )
    
    class Meta:
        unique_together = ('student', 'course_offering')
    
    def __str__(self):
        return f"{self.student.student_id} - {self.course_offering.module.code}"


# ==================== 9. LECTURER WORKLOAD & ATTENDANCE ====================

class ClassAttendance(models.Model):
    """Track attendance for classes"""
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    
    attendance_date = models.DateField()
    is_present = models.BooleanField(default=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ('course_offering', 'student', 'attendance_date')
    
    def __str__(self):
        return f"{self.student.student_id} - {self.attendance_date}"


class Assignment(models.Model):
    """Assignment management for lecturers"""
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='assignments')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    status = models.CharField(
        max_length=20,
        choices=[('open', 'Open'), ('closed', 'Closed'), ('graded', 'Graded')],
        default='open'
    )
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    """Student assignment submissions"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_cascade=models.CASCADE, related_name='assignment_submissions')
    
    submission_file = models.FileField(upload_to='assignments/')
    submission_date = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)
    
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    graded_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ('assignment', 'student')
    
    def __str__(self):
        return f"{self.student.student_id} - {self.assignment.title}"


class GradeSubmissionDeadline(models.Model):
    """Reminders for grade submission deadlines"""
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10)
    
    deadline_type = models.CharField(
        max_length=20,
        choices=[('midterm', 'Midterm'), ('final', 'Final')],
    )
    
    deadline_date = models.DateField()
    
    reminder_days_before = models.IntegerField(default=7)  # Send reminder 7 days before
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('academic_year', 'semester', 'deadline_type')
    
    def __str__(self):
        return f"{self.academic_year} {self.deadline_type.title()} Deadline"


# ==================== 10. ACADEMIC CALENDAR ====================

class AcademicCalendar(models.Model):
    """System-wide academic calendar"""
    academic_year = models.CharField(max_length=20, unique=True)
    
    YEAR_STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=YEAR_STATUS_CHOICES, default='planning')
    
    # Year dates
    year_start_date = models.DateField()
    year_end_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.academic_year


class AcademicCalendarEvent(models.Model):
    """Important dates and events in the academic calendar"""
    EVENT_TYPE_CHOICES = [
        ('registration', 'Registration'),
        ('exam', 'Exam Period'),
        ('holiday', 'Holiday'),
        ('deadline', 'Deadline'),
        ('event', 'Event'),
        ('recess', 'Recess'),
    ]
    
    calendar = models.ForeignKey(AcademicCalendar, on_delete=models.CASCADE, related_name='events')
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    is_holiday = models.BooleanField(default=False)
    affects_classes = models.BooleanField(default=False)
    
    semester = models.CharField(max_length=10, blank=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} ({self.calendar.academic_year})"


class SemesterConfiguration(models.Model):
    """Configuration for each semester"""
    calendar = models.ForeignKey(AcademicCalendar, on_delete=models.CASCADE, related_name='semesters')
    
    semester = models.CharField(max_length=10)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    classes_start = models.DateField()
    classes_end = models.DateField()
    
    exam_start = models.DateField()
    exam_end = models.DateField()
    
    is_active = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('calendar', 'semester')
    
    def __str__(self):
        return f"{self.calendar.academic_year} - Semester {self.semester}"


# ==================== 11. PARENT/GUARDIAN PORTAL ====================

class ParentGuardian(models.Model):
    """Parent/Guardian account linked to student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardians')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    relationship = models.CharField(
        max_length=20,
        choices=[('parent', 'Parent'), ('guardian', 'Guardian'), ('sponsor', 'Sponsor')]
    )
    
    can_view_results = models.BooleanField(default=True)
    can_view_attendance = models.BooleanField(default=True)
    can_receive_alerts = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student.student_id})"


class GuardianAlert(models.Model):
    """Alerts sent to parents/guardians"""
    guardian = models.ForeignKey(ParentGuardian, on_cascade=models.CASCADE, related_name='alerts')
    
    ALERT_TYPE_CHOICES = [
        ('grade_warning', 'Grade Warning'),
        ('poor_attendance', 'Poor Attendance'),
        ('failing_course', 'Failing Course'),
        ('achievement', 'Academic Achievement'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    is_sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Alert to {self.guardian.first_name}"


# ==================== 12. QUALITY ASSURANCE & AUDIT ====================

class GradeAuditLog(models.Model):
    """Audit trail for all grade changes"""
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='audit_logs')
    
    CHANGE_TYPE_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('published', 'Published'),
        ('unpublished', 'Unpublished'),
    ]
    
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    old_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    new_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    old_grade = models.CharField(max_length=5, blank=True)
    new_grade = models.CharField(max_length=5, blank=True)
    
    reason = models.TextField(blank=True)
    
    changed_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_date']
    
    def __str__(self):
        return f"{self.result} - {self.change_type}"


class DataValidationRule(models.Model):
    """Define validation rules for data integrity"""
    rule_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Rule logic (will be evaluated in code)
    rule_type = models.CharField(
        max_length=20,
        choices=[
            ('score_range', 'Score Range'),
            ('gpa_range', 'GPA Range'),
            ('attendance_percent', 'Attendance Percentage'),
            ('unique_constraint', 'Unique Constraint'),
        ]
    )
    
    min_value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    max_value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.rule_name


class DataIntegrityReport(models.Model):
    """Reports on data integrity issues"""
    report_date = models.DateTimeField(auto_now_add=True)
    
    ISSUE_LEVEL_CHOICES = [
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    issue_level = models.CharField(max_length=20, choices=ISSUE_LEVEL_CHOICES)
    issue_type = models.CharField(max_length=100)
    description = models.TextField()
    
    affected_records = models.IntegerField(default=0)
    suggested_action = models.TextField(blank=True)
    
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-report_date']
    
    def __str__(self):
        return f"{self.issue_type} - {self.report_date.date()}"


# ==================== 13. API ENHANCEMENTS ====================

class APIIntegration(models.Model):
    """Track third-party API integrations"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    endpoint_url = models.URLField()
    api_key = models.CharField(max_length=500, blank=True)
    
    INTEGRATION_TYPE_CHOICES = [
        ('hris', 'HRIS System'),
        ('finance', 'Finance System'),
        ('portal', 'Portal'),
        ('communication', 'Communication'),
        ('other', 'Other'),
    ]
    
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPE_CHOICES)
    
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class WebhookConfiguration(models.Model):
    """Webhook configurations for event triggers"""
    name = models.CharField(max_length=100)
    
    EVENT_TYPE_CHOICES = [
        ('result_published', 'Result Published'),
        ('grade_changed', 'Grade Changed'),
        ('student_enrolled', 'Student Enrolled'),
        ('transcript_requested', 'Transcript Requested'),
    ]
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    webhook_url = models.URLField()
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event_type', 'webhook_url')
    
    def __str__(self):
        return self.name


class APIRateLimit(models.Model):
    """Rate limiting for API protection"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='api_rate_limit')
    
    requests_per_hour = models.IntegerField(default=100)
    requests_per_day = models.IntegerField(default=1000)
    
    current_hour_requests = models.IntegerField(default=0)
    current_day_requests = models.IntegerField(default=0)
    
    hour_reset_time = models.DateTimeField(auto_now=True)
    day_reset_time = models.DateTimeField(auto_now=True)
    
    is_blocked = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Rate Limit - {self.user.username}"


# ==================== 14. CURRICULUM MANAGEMENT ====================

class ProgramCurriculum(models.Model):
    """Curriculum version for a program"""
    program = models.ForeignKey(Program, on_cascade=models.CASCADE, related_name='curriculums')
    
    version = models.IntegerField(default=1)
    academic_year_introduced = models.CharField(max_length=20)
    
    total_credits = models.IntegerField()
    total_courses = models.IntegerField()
    
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('program', 'version')
    
    def __str__(self):
        return f"{self.program.name} v{self.version}"


class CurriculumCourse(models.Model):
    """Courses within a curriculum"""
    curriculum = models.ForeignKey(ProgramCurriculum, on_cascade=models.CASCADE, related_name='courses')
    module = models.ForeignKey(Module, on_cascade=models.CASCADE)
    
    COURSE_CATEGORY_CHOICES = [
        ('required', 'Required'),
        ('elective', 'Elective'),
        ('optional', 'Optional'),
    ]
    
    category = models.CharField(max_length=20, choices=COURSE_CATEGORY_CHOICES)
    semester = models.IntegerField()  # Which semester the course is typically taken
    
    class Meta:
        unique_together = ('curriculum', 'module')
    
    def __str__(self):
        return f"{self.curriculum} - {self.module.code}"


class CourseLearningOutcome(models.Model):
    """Learning outcomes for courses"""
    module = models.ForeignKey(Module, on_cascade=models.CASCADE, related_name='learning_outcomes')
    
    outcome_description = models.TextField()
    outcome_number = models.IntegerField()
    
    class Meta:
        unique_together = ('module', 'outcome_number')
    
    def __str__(self):
        return f"{self.module.code} - Outcome {self.outcome_number}"


class DegreeRequirement(models.Model):
    """Overall degree requirements"""
    program = models.OneToOneField(Program, on_cascade=models.CASCADE, related_name='degree_requirement')
    
    minimum_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=2.0)
    minimum_credits = models.IntegerField()
    
    # Specific requirements
    required_major_credits = models.IntegerField(default=0)
    required_elective_credits = models.IntegerField(default=0)
    required_general_ed_credits = models.IntegerField(default=0)
    
    max_years_to_complete = models.IntegerField(default=4)
    
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.program.name} Degree Requirements"


# ==================== 15. STUDENT PROGRESSION TRACKING ====================

class StudentProgression(models.Model):
    """Track student progression through their program"""
    student = models.OneToOneField(Student, on_cascade=models.CASCADE, related_name='progression')
    curriculum = models.ForeignKey(ProgramCurriculum, on_cascade=models.CASCADE)
    
    enrollment_academic_year = models.CharField(max_length=20)
    
    current_curriculum_semester = models.IntegerField(default=1)  # Which semester in curriculum
    
    expected_graduation_year = models.IntegerField(blank=True, null=True)
    actual_graduation_year = models.IntegerField(blank=True, null=True)
    
    is_on_track = models.BooleanField(default=True)
    off_track_reason = models.CharField(max_length=200, blank=True)
    
    has_graduated = models.BooleanField(default=False)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.student_id} Progression"


class RetakeCourse(models.Model):
    """Track students retaking courses"""
    student = models.ForeignKey(Student, on_cascade=models.CASCADE, related_name='retaken_courses')
    module = models.ForeignKey(Module, on_cascade=models.CASCADE)
    
    original_academic_year = models.CharField(max_length=20)
    original_semester = models.CharField(max_length=10)
    original_grade = models.CharField(max_length=5)
    original_score = models.DecimalField(max_digits=5, decimal_places=2)
    
    retake_academic_year = models.CharField(max_length=20)
    retake_semester = models.CharField(max_length=10)
    retake_grade = models.CharField(max_length=5, blank=True)
    retake_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    reason_for_retake = models.CharField(
        max_length=100,
        choices=[('improve_grade', 'Improve Grade'), ('failed', 'Failed'), ('other', 'Other')]
    )
    
    class Meta:
        unique_together = ('student', 'module', 'retake_academic_year', 'retake_semester')
    
    def __str__(self):
        return f"{self.student.student_id} - {self.module.code} Retake"


class GraduationEligibility(models.Model):
    """Track graduation eligibility for students"""
    student = models.OneToOneField(Student, on_cascade=models.CASCADE, related_name='graduation_eligibility')
    
    is_eligible = models.BooleanField(default=False)
    
    credits_completed = models.IntegerField(default=0)
    credits_required = models.IntegerField()
    
    gpa_requirement_met = models.BooleanField(default=False)
    current_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    required_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=2.0)
    
    all_required_courses_completed = models.BooleanField(default=False)
    
    outstanding_courses = models.ManyToManyField(Module, blank=True, related_name='students_needing_completion')
    
    eligibility_checked_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.student_id} Graduation Eligibility"


class CohortAnalysis(models.Model):
    """Analyze cohort (group) of students"""
    cohort_name = models.CharField(max_length=100)
    program = models.ForeignKey(Program, on_cascade=models.CASCADE, related_name='cohort_analyses')
    
    enrollment_academic_year = models.CharField(max_length=20)
    cohort_size = models.IntegerField(default=0)
    
    average_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    graduation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    average_time_to_graduation = models.DecimalField(max_digits=3, decimal_places=1, default=0)  # years
    
    dropout_count = models.IntegerField(default=0)
    
    analysis_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Detailed statistics as JSON
    statistics = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ('cohort_name', 'program', 'enrollment_academic_year')
    
    def __str__(self):
        return self.cohort_name
