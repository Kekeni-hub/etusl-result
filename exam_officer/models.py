from django.db import models
from django.contrib.auth.models import User

class ExamOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='exam_officer_profile')
    officer_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.officer_id})"


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('result', 'Result Published'),
        ('report', 'Report'),
        ('system', 'System Notice'),
        ('warning', 'Warning'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notifications_created')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SystemReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('student_results', 'Student Results Report'),
        ('lecturer_upload', 'Lecturer Upload Report'),
        ('published_results', 'Published Results Report'),
        ('system', 'System Report'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    faculty = models.ForeignKey('student.Faculty', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('student.Department', on_delete=models.SET_NULL, null=True, blank=True)
    program = models.ForeignKey('student.Program', on_delete=models.SET_NULL, null=True, blank=True)
    
    generated_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-generated_date']

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"

