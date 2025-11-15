from django.core.management.base import BaseCommand
from student.models import StudentSemesterFolder


class Command(BaseCommand):
    help = 'Calculate GPA and total score for all student semester folders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--student-id',
            type=str,
            help='Calculate GPA for a specific student ID',
        )
        parser.add_argument(
            '--folder-id',
            type=int,
            help='Calculate GPA for a specific semester folder ID',
        )

    def handle(self, *args, **options):
        student_id = options.get('student_id')
        folder_id = options.get('folder_id')

        if folder_id:
            try:
                folder = StudentSemesterFolder.objects.get(id=folder_id)
                folder.recalculate_all()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Calculated GPA and total score for {folder.student.student_id} '
                        f'({folder.academic_year} S{folder.semester}): '
                        f'Total Score: {folder.total_score}, GPA: {folder.gpa}'
                    )
                )
            except StudentSemesterFolder.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Folder with ID {folder_id} not found')
                )
        elif student_id:
            # Calculate for all semesters of a specific student
            folders = StudentSemesterFolder.objects.filter(student__student_id=student_id)
            if not folders.exists():
                self.stdout.write(
                    self.style.ERROR(f'No folders found for student {student_id}')
                )
                return
            
            for folder in folders:
                folder.recalculate_all()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {folder.student.student_id} ({folder.academic_year} S{folder.semester}): '
                        f'Total Score: {folder.total_score}, GPA: {folder.gpa}'
                    )
                )
        else:
            # Calculate for all folders
            folders = StudentSemesterFolder.objects.all()
            total = folders.count()
            for i, folder in enumerate(folders, 1):
                folder.recalculate_all()
                self.stdout.write(
                    f'[{i}/{total}] {folder.student.student_id} ({folder.academic_year} S{folder.semester}): '
                    f'Total Score: {folder.total_score}, GPA: {folder.gpa}'
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Completed! Calculated GPA and total scores for {total} semester folders.'
                )
            )
