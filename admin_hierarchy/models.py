from django.db import models
from django.contrib.auth.models import User
from student.models import Faculty, Department, Result


class HeadOfDepartment(models.Model):
    """HOD - Head of Department (manages students in a department)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hod_profile')
    hod_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.OneToOneField(Department, on_delete=models.SET_NULL, null=True, related_name='hod')
    office_location = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"HOD: {self.user.get_full_name()} ({self.department.name if self.department else 'N/A'})"


class DeanOfFaculty(models.Model):
    """DEAN - Faculty Administrator (reviews department submissions)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dean_profile')
    dean_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    faculty = models.OneToOneField(Faculty, on_delete=models.SET_NULL, null=True, related_name='dean')
    office_location = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"DEAN: {self.user.get_full_name()} ({self.faculty.name if self.faculty else 'N/A'})"


class ResultApprovalWorkflow(models.Model):
    """Track result submission through approval chain"""
    STATUS_CHOICES = [
        ('lecturer_submitted', 'Lecturer Submitted (Awaiting HOD)'),
        ('hod_approved', 'HOD Approved (Awaiting DEAN)'),
        ('hod_rejected', 'HOD Rejected'),
        ('dean_approved', 'DEAN Approved (Awaiting EXAM)'),
        ('dean_rejected', 'DEAN Rejected'),
        ('exam_published', 'EXAM Published'),
        ('exam_rejected', 'EXAM Rejected'),
    ]

    result = models.OneToOneField(Result, on_delete=models.CASCADE, related_name='approval_workflow')
    
    # Current status in workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lecturer_submitted')
    
    # Tracking which admin is currently responsible
    current_hod = models.ForeignKey(HeadOfDepartment, on_delete=models.SET_NULL, null=True, blank=True, related_name='pending_hod_approvals')
    current_dean = models.ForeignKey(DeanOfFaculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='pending_dean_approvals')
    current_exam_officer = models.ForeignKey('exam_officer.ExamOfficer', on_delete=models.SET_NULL, null=True, blank=True, related_name='pending_exam_approvals')
    
    # Approval/rejection notes
    hod_notes = models.TextField(blank=True, null=True)
    dean_notes = models.TextField(blank=True, null=True)
    exam_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    lecturer_submitted_at = models.DateTimeField(auto_now_add=True)
    hod_reviewed_at = models.DateTimeField(blank=True, null=True)
    dean_reviewed_at = models.DateTimeField(blank=True, null=True)
    exam_reviewed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-lecturer_submitted_at']

    def __str__(self):
        return f"{self.result} - {self.get_status_display()}"


class ApprovalHistory(models.Model):
    """Audit log of all approval actions"""
    workflow = models.ForeignKey(ResultApprovalWorkflow, on_delete=models.CASCADE, related_name='history')
    
    ACTION_CHOICES = [
        ('hod_approved', 'HOD Approved'),
        ('hod_rejected', 'HOD Rejected'),
        ('dean_approved', 'DEAN Approved'),
        ('dean_rejected', 'DEAN Rejected'),
        ('exam_published', 'EXAM Published'),
        ('exam_rejected', 'EXAM Rejected'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} by {self.admin_user.get_full_name()}"


class DeviceToken(models.Model):
    """Store FCM device tokens associated with a Django user."""
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='other')
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.platform} ({self.token[:8]}...)"
