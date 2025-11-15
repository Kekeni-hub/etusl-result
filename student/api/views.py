from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from student.models import Student, Result, Module, Assessment
from .serializers import StudentSerializer, ResultSerializer
from rest_framework.authtoken.models import Token
from admin_hierarchy.models import ResultApprovalWorkflow, HeadOfDepartment
import json

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.filter(is_active=True).select_related('user', 'faculty', 'department', 'program')
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all().select_related('student', 'program', 'department', 'faculty')
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # set uploaded_by if request user is a lecturer
        lecturer = getattr(self.request.user, 'lecturer_profile', None)
        serializer.save(uploaded_by=lecturer)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        # mark as submitted into workflow (simple status change)
        result = self.get_object()
        # Create or update the workflow: simplified from existing logic
        hod = HeadOfDepartment.objects.filter(department=result.student.department, is_active=True).first()
        if hod:
            ResultApprovalWorkflow.objects.update_or_create(
                result=result,
                defaults={'status': 'lecturer_submitted', 'current_hod': hod}
            )
            return Response({'status': 'submitted'})
        return Response({'status': 'no_hod_assigned'}, status=400)

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """
        Bulk upload assessments via JSON payload.
        Expected POST body (JSON):
        [
          {
            "student_id": 123,
            "module_id": 10,
            "academic_year": "2024/2025",
            "semester": "1",
            "assessments": {"exam": {"score": 45, "total": 100}, "test": {"score": 8, "total": 10}}
          }, ...
        ]
        """
        # Parse request body as JSON
        try:
            if isinstance(request.data, str):
                payload = json.loads(request.data)
            else:
                payload = request.data
        except Exception as e:
            return Response({'error': f'Invalid JSON: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(payload, list):
            return Response({'error': 'Payload must be a list of entries'}, status=status.HTTP_400_BAD_REQUEST)

        lecturer = getattr(request.user, 'lecturer_profile', None)
        if not lecturer:
            return Response({'error': 'User must be a lecturer'}, status=status.HTTP_403_FORBIDDEN)

        created_count = 0
        errors = []

        for idx, entry in enumerate(payload):
            try:
                student_id = entry.get('student_id')
                module_id = entry.get('module_id')
                academic_year = entry.get('academic_year')
                semester = entry.get('semester')
                assessments = entry.get('assessments', {})

                if not student_id or not module_id:
                    errors.append(f'Entry {idx}: missing student_id or module_id')
                    continue

                student = Student.objects.get(id=student_id)
                module = Module.objects.get(id=module_id)

                # Create Assessment rows
                for atype, adata in assessments.items():
                    try:
                        score = float(adata.get('score', 0))
                    except Exception:
                        score = 0
                    try:
                        total = float(adata.get('total', adata.get('total_score', 100)))
                    except Exception:
                        total = 100

                    Assessment.objects.create(
                        student=student,
                        module=module,
                        assessment_type=atype,
                        score=score,
                        total_score=total,
                        uploaded_by=lecturer,
                        academic_year=academic_year,
                        semester=semester,
                    )
                    created_count += 1

                # Recalculate or create module-level Result
                result = Result.objects.filter(
                    student=student,
                    subject=module.name,
                    academic_year=academic_year,
                    semester=semester
                ).first()

                if not result:
                    result = Result.objects.create(
                        student=student,
                        subject=module.name,
                        program=module.program,
                        department=module.department,
                        faculty=module.faculty,
                        result_type='module',
                        academic_year=academic_year,
                        semester=semester,
                        score=0,
                        total_score=100,
                        grade='F',
                        uploaded_by=lecturer,
                    )

                # Try to recalculate from assessments
                try:
                    result.recalculate_from_assessments()
                except Exception as e:
                    pass  # If recalculate fails, result remains as-is

                # Create/update workflow
                hod = HeadOfDepartment.objects.filter(
                    department=student.department,
                    is_active=True
                ).first()
                if hod:
                    ResultApprovalWorkflow.objects.update_or_create(
                        result=result,
                        defaults={'status': 'lecturer_submitted', 'current_hod': hod}
                    )

            except Student.DoesNotExist:
                errors.append(f'Entry {idx}: Student {student_id} not found')
            except Module.DoesNotExist:
                errors.append(f'Entry {idx}: Module {module_id} not found')
            except Exception as e:
                errors.append(f'Entry {idx}: {str(e)}')

        return Response({
            'created_assessments': created_count,
            'total_entries': len(payload),
            'errors': errors
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)


class TokenRotateView(APIView):
    """Rotate (recreate) token for the authenticated user and return the new token."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        # Delete existing tokens
        Token.objects.filter(user=user).delete()
        # Create a new token
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

