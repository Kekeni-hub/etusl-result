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
    must_change_password = models.BooleanField(default=False)

    class Meta:
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class StudentSemesterFolder(models.Model):
    """Represents a container/folder for all a student's results for a specific
    academic year and semester. This allows grouping results for display and
    avoids scattered entries when multiple lecturers upload assessments."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='semester_folders')
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20, choices=[('1', 'Semester 1'), ('2', 'Semester 2')])
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    
    # GPA and total score fields
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # 0.0 - 5.0 or 0.0 - 4.0
    is_gpa_calculated = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'academic_year', 'semester')

    def __str__(self):
        return f"{self.student.student_id} - {self.academic_year} S{self.semester}"

    def calculate_total_score(self):
        """Calculate the total score for this semester folder (average of all results)."""
        results = self.results.filter(is_published=True)
        if not results.exists():
            self.total_score = 0
            return 0
        
        avg_score = sum([float(r.score) for r in results]) / results.count()
        self.total_score = round(avg_score, 2)
        return self.total_score

    def calculate_gpa(self, scale=4.0):
        """
        Calculate GPA from semester results using a standard 4.0 scale.
        Grade mappings:
        - A (80-100): 4.0
        - B (70-79):  3.0
        - C (60-69):  2.0
        - D (50-59):  1.0
        - F (<50):    0.0
        """
        results = self.results.filter(is_published=True)
        if not results.exists():
            self.gpa = 0
            return 0
        
        # Map grades to GPA points
        grade_to_gpa = {
            'A': 4.0,
            'B': 3.0,
            'C': 2.0,
            'D': 1.0,
            'F': 0.0,
        }
        
        total_gpa = 0
        count = 0
        for result in results:
            grade = result.grade or 'F'
            gpa_point = grade_to_gpa.get(grade, 0.0)
            total_gpa += gpa_point
            count += 1
        
        if count > 0:
            self.gpa = round(total_gpa / count, 2)
        else:
            self.gpa = 0
        
        self.is_gpa_calculated = True
        return self.gpa

    def recalculate_all(self):
        """Recalculate both total score and GPA for this semester folder."""
        self.calculate_total_score()
        self.calculate_gpa()
        self.save()



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
    # Folder linking: groups all results for a student in a particular academic year + semester
    folder = models.ForeignKey('StudentSemesterFolder', on_delete=models.CASCADE, null=True, blank=True, related_name='results')
    
    uploaded_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_date']
        unique_together = ('student', 'subject', 'result_type', 'academic_year', 'semester')

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.result_type})"

    def save(self, *args, **kwargs):
        # Ensure this Result is assigned to the correct StudentSemesterFolder
        try:
            if not self.folder and self.student and self.academic_year and self.semester:
                folder, _ = StudentSemesterFolder.objects.get_or_create(
                    student=self.student,
                    academic_year=self.academic_year,
                    semester=self.semester,
                    defaults={
                        'program': self.program,
                        'department': self.department,
                        'faculty': self.faculty,
                    }
                )
                self.folder = folder
        except Exception:
            pass
        super().save(*args, **kwargs)

class Module(models.Model):
    """A course/module offered by a Program/Department/Faculty"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='modules')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='modules')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='modules')
    credits = models.IntegerField(default=3)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('exam', 'Exam'),
        ('test', 'Test'),
        ('assignment', 'Assignment'),
        ('attendance', 'Attendance'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assessments')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    score = models.DecimalField(max_digits=7, decimal_places=2)
    total_score = models.DecimalField(max_digits=7, decimal_places=2, default=100)
    uploaded_by = models.ForeignKey('lecturer.Lecturer', on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=10)
    uploaded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_date']
        unique_together = ('student', 'module', 'assessment_type', 'academic_year', 'semester')

    def __str__(self):
        return f"{self.student} - {self.module.code} [{self.assessment_type}] {self.score}/{self.total_score}"

    @property
    def percentage(self):
        try:
            return (float(self.score) / float(self.total_score)) * 100 if float(self.total_score) else 0
        except Exception:
            return 0

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # After saving an assessment, update the aggregate Result for the student-module
        try:
            # Ensure the student's semester folder exists and attach it to the Result
            folder, _ = StudentSemesterFolder.objects.get_or_create(
                student=self.student,
                academic_year=self.academic_year,
                semester=self.semester,
                defaults={
                    'program': self.module.program,
                    'department': self.module.department,
                    'faculty': self.module.faculty,
                }
            )

            Result.objects.update_or_create(
                student=self.student,
                subject=self.module.name,
                result_type='exam',
                academic_year=self.academic_year,
                semester=self.semester,
                defaults={
                    'program': self.module.program,
                    'department': self.module.department,
                    'faculty': self.module.faculty,
                    'uploaded_by': self.uploaded_by,
                    'folder': folder,
                }
            )
        except Exception:
            pass

def calculate_grade_from_percentage(percentage: float) -> str:
    if percentage >= 80:
        return 'A'
    if percentage >= 70:
        return 'B'
    if percentage >= 60:
        return 'C'
    if percentage >= 50:
        return 'D'
    return 'F'

# Attach aggregation helper to Result via monkey-patch-like addition
def result_recalculate_from_assessments(self):
    """Recalculate this Result's score and grade from related Assessment objects.
    We use fixed weights: exam 50%, test 20%, assignment 20%, attendance 10%.
    If an assessment type is missing, its weight is redistributed proportionally among present types.
    """
    weights = {'exam': 0.5, 'test': 0.2, 'assignment': 0.2, 'attendance': 0.1}
    # fetch assessments for this student/module/year/semester
    assessments = Assessment.objects.filter(
        student=self.student,
        module__name__iexact=self.subject,
        academic_year=self.academic_year,
        semester=self.semester
    )
    if not assessments.exists():
        return

    # group available types
    types_present = {a.assessment_type for a in assessments}
    total_weight_present = sum(weights[t] for t in types_present if t in weights)
    if total_weight_present == 0:
        total_weight_present = 1

    # compute weighted percentage
    total_percentage = 0.0
    for a_type in types_present:
        type_assessments = assessments.filter(assessment_type=a_type)
        # average percentage for this type
        avg_pct = 0.0
        count = type_assessments.count()
        if count:
            avg_pct = sum([float(x.percentage) for x in type_assessments]) / count
        # redistributed weight
        weight = weights.get(a_type, 0) / total_weight_present
        total_percentage += avg_pct * weight

    grade = calculate_grade_from_percentage(total_percentage)
    # update Result model fields
    try:
        self.score = round(total_percentage, 2)
        self.total_score = 100
        self.grade = grade
        self.save()
    except Exception:
        pass

# attach method
Result.recalculate_from_assessments = result_recalculate_from_assessments

