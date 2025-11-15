from rest_framework import serializers
from student.models import Student, Result

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'full_name', 'email', 'faculty', 'department', 'program', 'current_year']


class ResultSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), write_only=True, source='student')

    class Meta:
        model = Result
        fields = ['id', 'student', 'student_id', 'program', 'department', 'faculty', 'subject', 'result_type', 'score', 'total_score', 'grade', 'academic_year', 'semester', 'is_published']
