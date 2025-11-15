"""
DRF Serializers for enhanced features
"""

from rest_framework import serializers
from student.models import Student, Result, Module, Program
from student.models_enhanced import (
    CumulativeGPA,
    Transcript,
    TranscriptRequest,
    StudentProgressTracker,
    StudentNotification,
    AcademicProbation,
    EarlyWarningAlert,
    CourseOffering,
    StudentEnrollment,
    ClassAttendance,
    Assignment,
    AssignmentSubmission,
    ParentGuardian,
    GradeDistributionSnapshot,
    ClassPerformanceMetrics,
)


class CumulativeGPASerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    academic_standing_display = serializers.CharField(source='get_academic_standing_display', read_only=True)
    
    class Meta:
        model = CumulativeGPA
        fields = ['id', 'student', 'student_name', 'overall_gpa', 'academic_standing', 'academic_standing_display', 'on_deans_list']


class TranscriptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = Transcript
        fields = ['id', 'student', 'student_name', 'transcript_type', 'is_signed', 'generated_date']


class TranscriptRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = TranscriptRequest
        fields = ['id', 'student', 'student_name', 'purpose', 'status', 'request_date', 'required_by_date']


class StudentProgressTrackerSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = StudentProgressTracker
        fields = ['id', 'student', 'student_name', 'completed_credits', 'credits_progress_percentage', 'is_eligible_for_graduation']


class StudentNotificationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = StudentNotification
        fields = ['id', 'student', 'student_name', 'subject', 'message', 'is_sent', 'is_read', 'created_at']


class AcademicProbationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = AcademicProbation
        fields = ['id', 'student', 'student_name', 'probation_start_date', 'reason', 'is_active', 'minimum_required_gpa']


class EarlyWarningAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = EarlyWarningAlert
        fields = ['id', 'student', 'student_name', 'alert_type', 'trigger_value', 'is_acknowledged', 'alert_date']


class CourseOfferingSerializer(serializers.ModelSerializer):
    module_code = serializers.CharField(source='module.code', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.user.get_full_name', read_only=True)
    
    class Meta:
        model = CourseOffering
        fields = ['id', 'module', 'module_code', 'module_name', 'lecturer_name', 'academic_year', 'semester', 'enrolled_students', 'max_students']


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    course_module = serializers.CharField(source='course_offering.module.code', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = StudentEnrollment
        fields = ['id', 'student', 'student_name', 'course_module', 'status', 'enrollment_date']


class ClassAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    course_code = serializers.CharField(source='course_offering.module.code', read_only=True)
    
    class Meta:
        model = ClassAttendance
        fields = ['id', 'student', 'student_name', 'course_code', 'attendance_date', 'is_present']


class AssignmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course_offering.module.code', read_only=True)
    
    class Meta:
        model = Assignment
        fields = ['id', 'course_code', 'title', 'due_date', 'max_score', 'status']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'student', 'student_name', 'assignment', 'assignment_title', 'submission_date', 'score', 'is_late']


class GradeDistributionSnapshotSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    
    class Meta:
        model = GradeDistributionSnapshot
        fields = [
            'id', 'academic_year', 'semester', 'program_name',
            'grade_a_count', 'grade_b_count', 'grade_c_count', 'grade_d_count', 'grade_f_count',
            'average_score', 'pass_rate'
        ]


class ClassPerformanceMetricsSerializer(serializers.ModelSerializer):
    module_code = serializers.CharField(source='module.code', read_only=True)
    
    class Meta:
        model = ClassPerformanceMetrics
        fields = [
            'id', 'module_code', 'academic_year', 'semester',
            'class_average', 'highest_score', 'lowest_score', 'std_deviation', 'pass_rate'
        ]


class ParentGuardianSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = ParentGuardian
        fields = ['id', 'student', 'student_name', 'first_name', 'last_name', 'email', 'phone', 'relationship']


# ==================== API VIEWSETS ====================

from rest_framework import viewsets, permissions

class CumulativeGPAViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing cumulative GPA data
    """
    queryset = CumulativeGPA.objects.all()
    serializer_class = CumulativeGPASerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Students can only see their own GPA
        if self.request.user.is_staff:
            return CumulativeGPA.objects.all()
        try:
            student = self.request.user.student_profile
            return CumulativeGPA.objects.filter(student=student)
        except:
            return CumulativeGPA.objects.none()


class TranscriptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing transcripts
    """
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Transcript.objects.all()
        try:
            student = self.request.user.student_profile
            return Transcript.objects.filter(student=student)
        except:
            return Transcript.objects.none()


class StudentProgressTrackerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing student progress tracking
    """
    queryset = StudentProgressTracker.objects.all()
    serializer_class = StudentProgressTrackerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return StudentProgressTracker.objects.all()
        try:
            student = self.request.user.student_profile
            return StudentProgressTracker.objects.filter(student=student)
        except:
            return StudentProgressTracker.objects.none()


class StudentNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing student notifications
    """
    queryset = StudentNotification.objects.all()
    serializer_class = StudentNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            student = self.request.user.student_profile
            return StudentNotification.objects.filter(student=student)
        except:
            return StudentNotification.objects.none()


class GradeDistributionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing grade distribution data (analytics)
    """
    queryset = GradeDistributionSnapshot.objects.all()
    serializer_class = GradeDistributionSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return GradeDistributionSnapshot.objects.none()
        return GradeDistributionSnapshot.objects.all()


class ClassPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing class performance metrics
    """
    queryset = ClassPerformanceMetrics.objects.all()
    serializer_class = ClassPerformanceMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return ClassPerformanceMetrics.objects.none()
        return ClassPerformanceMetrics.objects.all()


class CourseOfferingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing course offerings
    """
    queryset = CourseOffering.objects.filter(is_active=True)
    serializer_class = CourseOfferingSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentEnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing student enrollments
    """
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            student = self.request.user.student_profile
            return StudentEnrollment.objects.filter(student=student)
        except:
            return StudentEnrollment.objects.none()


class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for accessing assignments
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """
    API for managing assignment submissions
    """
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            student = self.request.user.student_profile
            return AssignmentSubmission.objects.filter(student=student)
        except:
            return AssignmentSubmission.objects.none()
