from django.db import models
from django.contrib.auth.models import User

class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.faculty.name}"


class Program(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Student(models.Model):
    YEAR_CHOICES = [
        (1, 'Year 1'),
        (2, 'Year 2'),
        (3, 'Year 3'),
        (4, 'Year 4'),
        (5, 'Year 5'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    current_year = models.IntegerField(choices=YEAR_CHOICES, default=1)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class Result(models.Model):
    RESULT_TYPE_CHOICES = [
        ('exam', 'Exam'),
        ('test', 'Test'),
        ('assignment', 'Assignment'),
        ('presentation', 'Presentation'),
        ('attendance', 'Attendance'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    
    subject = models.CharField(max_length=100)
    result_type = models.CharField(max_length=20, choices=RESULT_TYPE_CHOICES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    grade = models.CharField(max_length=5, blank=True)
    
    academic_year = models.CharField(max_length=20)  # e.g., "2023/2024"
    semester = models.CharField(max_length=20, choices=[('1', 'Semester 1'), ('2', 'Semester 2')])
    
    uploaded_by = models.ForeignKey('lecturer.Lecturer', on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)
    
    uploaded_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_date']
        unique_together = ('student', 'subject', 'result_type', 'academic_year', 'semester')

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.result_type})"

