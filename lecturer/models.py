from django.db import models
from django.contrib.auth.models import User

class Lecturer(models.Model):
    DEPARTMENT_CHOICES = [
        ('CS', 'Computer Science'),
        ('ENG', 'Engineering'),
        ('MED', 'Medicine'),
        ('LAW', 'Law'),
        ('BUS', 'Business'),
        ('SCI', 'Science'),
        ('ART', 'Arts'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
    lecturer_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    faculty = models.ForeignKey('student.Faculty', on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey('student.Department', on_delete=models.SET_NULL, null=True)
    
    specialization = models.CharField(max_length=100, blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.lecturer_id})"

