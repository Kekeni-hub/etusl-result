from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from Etu_student_result.decorators import require_profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.core import serializers
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import json

from .models import Lecturer
from .forms import LecturerProfileForm
from student.models import Student, Result, Faculty, Department, Program, Module, Assessment
from student.models_enhanced import LecturerResultReport, ResultSubmissionDeadline
from django.db.models import Q
from admin_hierarchy.models import ResultApprovalWorkflow, HeadOfDepartment
from student.models import StudentSemesterFolder
from django.db.models import Count


def lecturer_home(request):
    """Lecturer home page"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'lecturer_profile'):
            return redirect('lecturer_dashboard')
    return render(request, 'lecturer/lecturer_home.html')


@require_http_methods(["GET", "POST"])
def lecturer_register(request):
    """Lecturer registration"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'lecturer_profile'):
            return redirect('lecturer_dashboard')
    
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        lecturer_id = request.POST.get('lecturer_id')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone = request.POST.get('phone')
        faculty_id = request.POST.get('faculty')
        department_id = request.POST.get('department')
        specialization = request.POST.get('specialization')
        
        # Validate passwords
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('lecturer_register')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('lecturer_register')
        
        # Check if lecturer ID already exists
        if Lecturer.objects.filter(lecturer_id=lecturer_id).exists():
            messages.error(request, 'Lecturer ID already registered.')
            return redirect('lecturer_register')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create lecturer profile
            faculty = Faculty.objects.get(id=faculty_id) if faculty_id else None
            department = Department.objects.get(id=department_id) if department_id else None
            
            lecturer = Lecturer.objects.create(
                user=user,
                lecturer_id=lecturer_id,
                email=email,
                phone=phone,
                faculty=faculty,
                department=department,
                specialization=specialization,
                is_verified=False
            )
            
            messages.success(request, 'Registration successful! Please wait for admin verification.')
            return redirect('lecturer_login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('lecturer_register')
    
    context = {
        'faculties': faculties,
        'departments': departments,
    }
    return render(request, 'lecturer/lecturer_register.html', context)


@require_http_methods(["GET", "POST"])
def lecturer_login(request):
    """Lecturer login"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'lecturer_profile'):
            return redirect('lecturer_dashboard')
    
    if request.method == 'POST':
        # Accept username or email
        identifier = request.POST.get('identifier') or request.POST.get('email')
        password = request.POST.get('password')

        user = None
        if identifier:
            if '@' in identifier:
                user = User.objects.filter(email__iexact=identifier).first()
            else:
                user = User.objects.filter(username__iexact=identifier).first()

        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                try:
                    lecturer = Lecturer.objects.get(user=user)
                    if not lecturer.is_active:
                        messages.error(request, 'Your account has been deactivated.')
                        return redirect('lecturer_login')
                except Lecturer.DoesNotExist:
                    messages.error(request, 'Lecturer profile not found.')
                    return redirect('lecturer_login')

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome, {user.first_name}!')
                return redirect('lecturer_dashboard')
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'lecturer/lecturer_login.html')


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_dashboard(request):
    """Lecturer dashboard"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    # Get statistics
    total_uploads = Result.objects.filter(uploaded_by=lecturer).count()
    pending_uploads = Result.objects.filter(uploaded_by=lecturer, is_published=False).count()
    published_uploads = Result.objects.filter(uploaded_by=lecturer, is_published=True).count()
    
    # Recent uploads
    recent_uploads = Result.objects.filter(uploaded_by=lecturer).order_by('-uploaded_date')[:10]
    
    context = {
        'lecturer': lecturer,
        'total_uploads': total_uploads,
        'pending_uploads': pending_uploads,
        'published_uploads': published_uploads,
        'recent_uploads': recent_uploads,
    }
    
    return render(request, 'lecturer/lecturer_dashboard.html', context)


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_edit_profile(request):
    """Allow a lecturer to edit their profile information."""
    try:
        lecturer = request.user.lecturer_profile
    except Lecturer.DoesNotExist:
        return redirect('lecturer_login')

    if request.method == 'POST':
        form = LecturerProfileForm(request.POST, instance=lecturer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('lecturer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill first/last/email into form initial
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = LecturerProfileForm(instance=lecturer, initial=initial)

    return render(request, 'lecturer/lecturer_edit_profile.html', {'form': form, 'lecturer': lecturer})


@login_required(login_url='lecturer_login')
def upload_results(request):
    """Upload student results"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    if request.method == 'POST':
        # New mode: submit a JSON payload in `assessments_json` describing
        # per-student, per-module assessments. Format:
        # [
        #   {
        #     "student_id": 123,
        #     "module_code": "CS101",
        #     "academic_year": "2024/2025",
        #     "semester": "1",
        #     "assessments": {"exam": {"score": 45, "total": 100}, "test": {"score":10, "total":20}}
        #   }, ...
        # ]

        assessments_json = request.POST.get('assessments_json')
        if assessments_json:
            try:
                payload = json.loads(assessments_json)
            except Exception as e:
                messages.error(request, f'Invalid JSON payload: {e}')
                return redirect('upload_results')

            created_count = 0
            errors = []
            try:
                if not payload or len(payload) == 0:
                    messages.error(request, 'No assessment data provided. Please add at least one module with scores.')
                    return redirect('upload_results')
                
                for entry in payload:
                    student_id = entry.get('student_id')
                    module_code = entry.get('module_code', '').strip()
                    academic_year = entry.get('academic_year')
                    semester = entry.get('semester')
                    assessments = entry.get('assessments', {})

                    # Validate that we have assessments with data
                    if not assessments or len(assessments) == 0:
                        errors.append(f'No assessment scores provided for module {module_code}')
                        continue

                    # Accept either a module_code or a module_id; at least one must be present
                    if not module_code and not entry.get('module_id'):
                        errors.append('Module code or module_id missing in entry')
                        continue

                    try:
                        student = Student.objects.get(id=student_id)
                    except Student.DoesNotExist:
                        errors.append(f'Student ID {student_id} not found')
                        print(f'[DEBUG] student id {student_id} not found')
                        continue

                    # Resolve module: accept either module_id or module_code
                    module = None
                    module_id = entry.get('module_id')
                    if module_id:
                        try:
                            module = Module.objects.get(id=module_id)
                        except Module.DoesNotExist:
                            errors.append(f'Module id {module_id} not found; will try module code')

                    if not module:
                        # Try module_code next
                        try:
                            if module_code:
                                module = Module.objects.filter(code=module_code).first()
                        except Exception:
                            module = None

                    if not module:
                        # Create module if we have a code or fallback to a generic name
                        created_code = module_code if module_code else f'MOD_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                        module = Module.objects.create(
                            code=created_code,
                            name=module_code or created_code,
                            program=student.program,
                            department=student.department,
                            faculty=student.faculty,
                        )
                    # resolved module

                    # Create Assessment rows for each assessment type provided
                    for atype, adata in assessments.items():
                        try:
                            score = float(adata.get('score', 0))
                        except Exception:
                            score = 0
                        try:
                            total = float(adata.get('total', adata.get('total_score', 100)))
                        except Exception:
                            total = 100

                        try:
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
                        except Exception as e:
                            errors.append(f'Assessment creation error for {student.student_id} / {atype}: {str(e)}')

                    # After creating assessments for this student+module, recalculate module Result
                    try:
                        result, created = Result.objects.get_or_create(
                            student=student,
                            subject=module.name,
                            result_type='exam',
                            academic_year=academic_year,
                            semester=semester,
                            defaults={
                                'program': student.program,
                                'department': student.department,
                                'faculty': student.faculty,
                                'score': 0,
                                'total_score': 100,
                                'grade': 'F',
                                'uploaded_by': lecturer,
                            }
                        )
                        
                        try:
                            result.recalculate_from_assessments()
                        except Exception as e:
                            errors.append(f'Grade recalculation error for {student.student_id}: {str(e)}')
                    except Exception as e:
                        errors.append(f'Could not create/update result for {student.student_id} / {module_code}: {str(e)}')

                    # Ensure a workflow exists and is set to lecturer_submitted -> HOD
                    try:
                        hod = HeadOfDepartment.objects.filter(department=student.department, is_active=True).first()
                        if hod and result:
                            ResultApprovalWorkflow.objects.update_or_create(
                                result=result,
                                defaults={
                                    'status': 'lecturer_submitted',
                                    'current_hod': hod,
                                }
                            )
                    except Exception as e:
                        errors.append(f'Workflow error: {e}')

                if created_count == 0 and len(errors) > 0:
                    messages.error(request, f'Failed to upload results. Errors: ' + '; '.join(errors[:5]))
                    return redirect('upload_results')
                
                if errors:
                    messages.warning(request, f'Uploaded {created_count} entries with {len(errors)} warnings:\n' + '\n'.join(errors[:5]))
                else:
                    messages.success(request, f'Successfully uploaded {created_count} assessment entries. Waiting for HOD approval.')
                return redirect('lecturer_dashboard')
            except Exception as e:
                messages.error(request, f'Upload failed: {e}')
                return redirect('upload_results')

        # Fallback to legacy single-subject upload fields
        students = request.POST.getlist('students[]')
        program_id = request.POST.get('program')
        subject = request.POST.get('subject')
        result_type = request.POST.get('result_type')
        scores = request.POST.getlist('scores[]')
        total_score = request.POST.get('total_score', 100)
        academic_year = request.POST.get('academic_year')
        semester = request.POST.get('semester')

        try:
            program = Program.objects.get(id=program_id)

            for i, student_id in enumerate(students):
                student = Student.objects.get(id=student_id)
                score = float(scores[i]) if i < len(scores) else 0

                # Calculate grade
                percentage = (score / float(total_score)) * 100 if float(total_score) else 0
                if percentage >= 80:
                    grade = 'A'
                elif percentage >= 70:
                    grade = 'B'
                elif percentage >= 60:
                    grade = 'C'
                elif percentage >= 50:
                    grade = 'D'
                else:
                    grade = 'F'

                result, created = Result.objects.update_or_create(
                    student=student,
                    subject=subject,
                    result_type=result_type,
                    academic_year=academic_year,
                    semester=semester,
                    defaults={
                        'program': program,
                        'department': student.department,
                        'faculty': student.faculty,
                        'score': score,
                        'total_score': total_score,
                        'grade': grade,
                        'uploaded_by': lecturer,
                    }
                )

                hod = HeadOfDepartment.objects.filter(department=student.department, is_active=True).first()
                if hod:
                    workflow, _ = ResultApprovalWorkflow.objects.update_or_create(
                        result=result,
                        defaults={
                            'status': 'lecturer_submitted',
                            'current_hod': hod,
                        }
                    )

            messages.success(request, f'Successfully uploaded results for {len(students)} students. Waiting for HOD approval.')
            return redirect('lecturer_dashboard')
        except Exception as e:
            messages.error(request, f'Upload failed: {str(e)}')
    
    # Get programs, modules and students. Show ALL departments/programs for upload page
    programs = Program.objects.all()
    modules = Module.objects.all()

    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    
    # Build students queryset.
    # Previously we limited students to the lecturer's faculty/department/program.
    # Per request, list all active students in the system so lecturers can select
    # any student that the DEAN has added.
    students_qs = Student.objects.filter(is_active=True).select_related('user', 'faculty', 'department', 'program')

    # Convert students to JSON for JavaScript
    students_list = []
    for s in students_qs:
        students_list.append({
            'id': s.id,
            'label': f"{s.student_id} — {s.user.get_full_name()}"
        })
    students_json = json.dumps(students_list)

    # modules JSON for frontend
    modules_list = []
    for m in modules:
        modules_list.append({'id': m.id, 'code': m.code or '', 'name': m.name})
    modules_json = json.dumps(modules_list)

    # departments and programs JSON for frontend filtering
    departments_list = []
    for d in departments:
        departments_list.append({'id': d.id, 'name': d.name, 'faculty_id': d.faculty.id if d.faculty else None})
    departments_json = json.dumps(departments_list)

    programs_list = []
    for p in programs:
        programs_list.append({'id': p.id, 'name': p.name, 'department_id': p.department.id if p.department else None})
    programs_json = json.dumps(programs_list)

    context = {
        'programs': programs,
        'result_types': [('exam', 'Exam'), ('test', 'Test'), ('assignment', 'Assignment'),
                         ('presentation', 'Presentation'), ('attendance', 'Attendance')],
        'current_year': datetime.now().year,
        'students': students_qs,
        'students_json': students_json,
        'modules': modules,
        'modules_json': modules_json,
        'departments_json': departments_json,
        'programs_json': programs_json,
        'faculties': faculties,
        'departments': departments,
    }
    
    return render(request, 'lecturer/upload_results.html', context)


def lecturer_logout(request):
    """Lecturer logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('lecturer_home')


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_uploads_by_program(request):
    """List programs for which the lecturer has uploaded results, grouped with counts."""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')

    qs = Result.objects.filter(uploaded_by=lecturer).select_related('program')
    groups = qs.values('program__id', 'program__name').annotate(count=Count('id')).order_by('-count')
    groups_list = []
    for g in groups:
        groups_list.append({
            'program_id': g['program__id'],
            'program_name': g['program__name'],
            'count': g['count']
        })

    return render(request, 'lecturer/uploads_by_program.html', {'groups': groups_list})


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_program_results(request, program_id):
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')

    program = get_object_or_404(Program, id=program_id)
    results = Result.objects.filter(uploaded_by=lecturer, program=program).select_related('student').order_by('-uploaded_date')

    return render(request, 'lecturer/program_results.html', {'program': program, 'results': results})


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_results_list(request):
    """List results uploaded by the lecturer with search and pagination"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')

    q = request.GET.get('q', '').strip()
    qs = Result.objects.filter(uploaded_by=lecturer).select_related('student', 'department')

    if q:
        qs = qs.filter(Q(student__student_id__icontains=q) | Q(subject__icontains=q))

    paginator = Paginator(qs.order_by('-uploaded_date'), 20)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    context = {
        'lecturer': lecturer,
        'page_obj': page,
        'results': page.object_list,
        'q': q,
    }
    return render(request, 'lecturer/results_list.html', context)


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_student_folders(request):
    """List student semester folders relevant to the lecturer (by department/program/faculty)."""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')

    qs = StudentSemesterFolder.objects.select_related('student', 'program', 'department', 'faculty')
    if lecturer.department:
        qs = qs.filter(student__department=lecturer.department)
    elif lecturer.faculty:
        qs = qs.filter(student__faculty=lecturer.faculty)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(student__student_id__icontains=q) | qs.filter(student__user__first_name__icontains=q) | qs.filter(student__user__last_name__icontains=q)

    qs = qs.order_by('-academic_year', '-semester', 'student__student_id')

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    context = {
        'lecturer': lecturer,
        'page_obj': page,
        'folders': page.object_list,
        'q': q,
    }
    return render(request, 'lecturer/student_folders.html', context)


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_folder_detail(request, folder_id):
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')

    folder = get_object_or_404(StudentSemesterFolder, id=folder_id)

    # permission: lecturer must belong to same department or faculty
    if lecturer.department and folder.student.department != lecturer.department:
        return redirect('lecturer_student_folders')
    if lecturer.faculty and folder.student.faculty != lecturer.faculty and not lecturer.department:
        return redirect('lecturer_student_folders')

    results = folder.results.select_related('uploaded_by', 'student').order_by('subject')

    context = {
        'lecturer': lecturer,
        'folder': folder,
        'results': results,
    }
    return render(request, 'lecturer/student_folder_detail.html', context)


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_edit_result(request, result_id):
    """Edit a single result (only by uploader). Confirmation required to save."""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')

    result = get_object_or_404(Result, id=result_id, uploaded_by=lecturer)

    if request.method == 'POST':
        # require an explicit confirmation param
        confirm = request.POST.get('confirm')
        if not confirm:
            messages.error(request, 'Please confirm the edit to proceed.')
            return redirect('lecturer_edit_result', result_id=result.id)

        try:
            score = float(request.POST.get('score', result.score))
            total_score = float(request.POST.get('total_score', result.total_score or 100))
            # Recalculate grade
            percentage = (score / float(total_score)) * 100 if total_score else 0
            if percentage >= 80:
                grade = 'A'
            elif percentage >= 70:
                grade = 'B'
            elif percentage >= 60:
                grade = 'C'
            elif percentage >= 50:
                grade = 'D'
            else:
                grade = 'F'

            result.score = score
            result.total_score = total_score
            result.grade = grade
            result.save()

            # update/create workflow back to lecturer_submitted (resubmit)
            hod = HeadOfDepartment.objects.filter(department=result.student.department, is_active=True).first()
            if hod:
                workflow, _ = ResultApprovalWorkflow.objects.update_or_create(
                    result=result,
                    defaults={
                        'status': 'lecturer_submitted',
                        'current_hod': hod,
                    }
                )

            messages.success(request, 'Result updated and submitted for HOD review.')
            return redirect('lecturer_results_list')
        except Exception as e:
            messages.error(request, f'Update failed: {e}')

    context = {
        'result': result,
        'lecturer': lecturer,
    }
    return render(request, 'lecturer/edit_result.html', context)


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_delete_result(request, result_id):
    """Delete a result (with confirmation). Only uploader can delete."""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')

    result = get_object_or_404(Result, id=result_id, uploaded_by=lecturer)

    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        if confirm:
            # delete associated workflow if exists
            try:
                if hasattr(result, 'approval_workflow'):
                    result.approval_workflow.delete()
            except Exception:
                pass
            result.delete()
            messages.success(request, 'Result deleted successfully.')
            return redirect('lecturer_results_list')
        else:
            messages.error(request, 'Please confirm deletion to proceed.')

    return render(request, 'lecturer/confirm_delete_result.html', {'result': result, 'lecturer': lecturer})


@require_profile('lecturer_profile', login_url='lecturer_login')
def lecturer_submit_result(request, result_id):
    """Explicitly (re)submit a result to create/update the approval workflow."""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')

    result = get_object_or_404(Result, id=result_id, uploaded_by=lecturer)

    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        if not confirm:
            messages.error(request, 'Please confirm submission to proceed.')
            return redirect('lecturer_results_list')

        hod = HeadOfDepartment.objects.filter(department=result.student.department, is_active=True).first()
        if not hod:
            messages.error(request, 'No active HOD assigned to the student department.')
            return redirect('lecturer_results_list')

        workflow, created = ResultApprovalWorkflow.objects.update_or_create(
            result=result,
            defaults={
                'status': 'lecturer_submitted',
                'current_hod': hod,
            }
        )
        messages.success(request, 'Result submitted to HOD for review.')
        return redirect('lecturer_results_list')

    # For GET, redirect to list
    return redirect('lecturer_results_list')


# ==================== LECTURER RESULT REPORTS ====================

@login_required(login_url='lecturer_login')
def lecturer_reports(request):
    """View all lecturer result reports"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    reports = lecturer.result_reports.all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    reports_page = paginator.get_page(page_number)
    
    context = {
        'reports_page': reports_page,
        'status_choices': [('draft', 'Draft'), ('submitted', 'Submitted'), ('reviewed', 'Reviewed'), ('approved', 'Approved'), ('rejected', 'Rejected')],
    }
    return render(request, 'lecturer/lecturer_reports.html', context)


@login_required(login_url='lecturer_login')
@require_http_methods(["GET", "POST"])
def create_result_report(request):
    """Create a new result report about unsatisfactory results"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    if request.method == 'POST':
        module_id = request.POST.get('module')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        report_title = request.POST.get('report_title')
        report_content = request.POST.get('report_content')
        severity_level = request.POST.get('severity_level')
        students_with_issues = request.POST.get('students_with_issues')
        average_score = request.POST.get('average_score')
        pass_rate = request.POST.get('pass_rate')
        recommended_actions = request.POST.get('recommended_actions')
        affected_students = request.POST.getlist('affected_students')
        
        try:
            module = Module.objects.get(id=module_id)
            
            report = LecturerResultReport.objects.create(
                lecturer=lecturer,
                module=module,
                semester=semester,
                academic_year=academic_year,
                report_title=report_title,
                report_content=report_content,
                severity_level=severity_level,
                students_with_issues=int(students_with_issues) if students_with_issues else 0,
                average_score=float(average_score) if average_score else 0,
                pass_rate=float(pass_rate) if pass_rate else 0,
                recommended_actions=recommended_actions,
                affected_students=affected_students,
                status='draft'
            )
            
            messages.success(request, 'Report created successfully. You can edit it before submission.')
            return redirect('view_result_report', report_id=report.id)
        except Exception as e:
            messages.error(request, f'Failed to create report: {str(e)}')
    
    modules = Module.objects.filter(lecturer__user=request.user)
    
    # Get students with their latest results for this lecturer
    students = Student.objects.filter(
        result__uploaded_by=lecturer
    ).distinct()
    
    context = {
        'modules': modules,
        'students': students,
    }
    return render(request, 'lecturer/create_result_report.html', context)


@login_required(login_url='lecturer_login')
def view_result_report(request, report_id):
    """View a result report"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    report = get_object_or_404(LecturerResultReport, id=report_id)
    
    # Check permission
    if report.lecturer != lecturer and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('lecturer_reports')
    
    context = {
        'report': report,
        'can_edit': report.status == 'draft' and report.lecturer == lecturer,
    }
    return render(request, 'lecturer/view_result_report.html', context)


@login_required(login_url='lecturer_login')
@require_http_methods(["POST"])
def edit_result_report(request, report_id):
    """Edit a result report (only if draft)"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    report = get_object_or_404(LecturerResultReport, id=report_id, lecturer=lecturer)
    
    if report.status != 'draft':
        messages.error(request, 'Cannot edit a report that has been submitted.')
        return redirect('view_result_report', report_id=report_id)
    
    # Update fields
    report.report_title = request.POST.get('report_title', report.report_title)
    report.report_content = request.POST.get('report_content', report.report_content)
    report.severity_level = request.POST.get('severity_level', report.severity_level)
    report.students_with_issues = int(request.POST.get('students_with_issues', report.students_with_issues) or 0)
    report.average_score = float(request.POST.get('average_score', report.average_score) or 0)
    report.pass_rate = float(request.POST.get('pass_rate', report.pass_rate) or 0)
    report.recommended_actions = request.POST.get('recommended_actions', report.recommended_actions)
    report.save()
    
    messages.success(request, 'Report updated successfully.')
    return redirect('view_result_report', report_id=report_id)


@login_required(login_url='lecturer_login')
@require_http_methods(["POST"])
def submit_result_report(request, report_id):
    """Submit a result report to HOD"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    report = get_object_or_404(LecturerResultReport, id=report_id, lecturer=lecturer)
    
    if report.status != 'draft':
        messages.error(request, 'Report has already been submitted.')
        return redirect('view_result_report', report_id=report_id)
    
    report.status = 'submitted'
    report.submitted_at = timezone.now()
    report.save()
    
    # Send notification to HOD
    hod = HeadOfDepartment.objects.filter(
        department=lecturer.department,
        is_active=True
    ).first()
    
    if hod and hod.user:
        from exam_officer.models import Notification
        Notification.objects.create(
            recipient=hod.user,
            notification_type='report',
            title='New Result Report from Lecturer',
            message=f'Lecturer {lecturer.user.get_full_name()} submitted a report on {report.module.module_code}: {report.report_title}',
            created_by=request.user,
        )
    
    messages.success(request, 'Report submitted to HOD for review.')
    return redirect('view_result_report', report_id=report_id)


# ==================== RESULT SUBMISSION DEADLINES ====================

@login_required(login_url='lecturer_login')
def submission_deadlines(request):
    """View result submission deadlines"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    # Get deadlines for lecturer's program
    deadlines = ResultSubmissionDeadline.objects.filter(
        program__department=lecturer.department,
        is_active=True
    ).order_by('deadline_date')
    
    context = {
        'deadlines': deadlines,
    }
    return render(request, 'lecturer/submission_deadlines.html', context)


# ==================== CSV BULK UPLOAD ====================

import csv
from io import StringIO, TextIOWrapper
from django.http import HttpResponse

@login_required(login_url='lecturer_login')
@require_http_methods(["GET", "POST"])
def upload_results_csv(request):
    """Upload results via CSV file, filtered by program and year"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    programs = Program.objects.all()
    result_types = [
        ('exam', 'Exam'),
        ('test', 'Test'),
        ('assignment', 'Assignment'),
        ('presentation', 'Presentation'),
        ('attendance', 'Attendance'),
        ('reference', 'Reference'),
        ('current_exam', 'Current Exam'),
        ('incomplete_grades', 'Incomplete Grades'),
    ]
    academic_years = [
        ('2023/2024', '2023/2024'),
        ('2024/2025', '2024/2025'),
        ('2025/2026', '2025/2026'),
    ]
    semesters = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
    ]
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        program_id = request.POST.get('program')
        result_type = request.POST.get('result_type')
        academic_year = request.POST.get('academic_year')
        semester = request.POST.get('semester')
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('upload_results_csv')
        
        if not program_id:
            messages.error(request, 'Please select a program.')
            return redirect('upload_results_csv')
        
        if not academic_year:
            messages.error(request, 'Please select an academic year.')
            return redirect('upload_results_csv')
        
        if not semester:
            messages.error(request, 'Please select a semester.')
            return redirect('upload_results_csv')
        
        if not result_type:
            messages.error(request, 'Please select a result type.')
            return redirect('upload_results_csv')
        
        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            messages.error(request, 'Invalid program selected.')
            return redirect('upload_results_csv')
        
        # Parse CSV
        try:
            csv_text = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(csv_text)
            
            if not reader.fieldnames:
                messages.error(request, 'CSV file is empty.')
                return redirect('upload_results_csv')
            
            # Validate headers
            required_headers = {'Student_ID', 'Module_Code', 'Score'}
            missing_headers = required_headers - set(reader.fieldnames or [])
            if missing_headers:
                messages.error(request, f'Missing required columns: {", ".join(missing_headers)}. Required: Student_ID, Module_Code, Score')
                return redirect('upload_results_csv')
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                try:
                    student_id = row.get('Student_ID', '').strip()
                    module_code = row.get('Module_Code', '').strip()
                    score_str = row.get('Score', '').strip()
                    total_score_str = row.get('Total_Score', '100').strip()
                    
                    # Validate fields
                    if not student_id:
                        errors.append(f'Row {row_num}: Student_ID is required')
                        continue
                    
                    if not module_code:
                        errors.append(f'Row {row_num}: Module_Code is required')
                        continue
                    
                    if not score_str:
                        errors.append(f'Row {row_num}: Score is required')
                        continue
                    
                    # Convert to numbers
                    try:
                        score = float(score_str)
                    except ValueError:
                        errors.append(f'Row {row_num}: Score "{score_str}" is not a valid number')
                        continue
                    
                    try:
                        total_score = float(total_score_str) if total_score_str else 100
                    except ValueError:
                        errors.append(f'Row {row_num}: Total_Score "{total_score_str}" is not a valid number')
                        continue
                    
                    # Find student by student_id (not Django user ID)
                    try:
                        student = Student.objects.get(student_id=student_id)
                    except Student.DoesNotExist:
                        errors.append(f'Row {row_num}: Student with ID {student_id} not found')
                        continue
                    
                    # Verify student belongs to selected program
                    if student.program.id != program.id:
                        errors.append(f'Row {row_num}: Student {student_id} is not in program {program.name}')
                        continue
                    
                    # Find or create module
                    module = Module.objects.filter(code=module_code).first()
                    if not module:
                        # Create module if it doesn't exist
                        module = Module.objects.create(
                            code=module_code,
                            name=module_code,
                            program=program,
                            department=student.department,
                            faculty=student.faculty,
                        )
                    
                    # Calculate grade
                    percentage = (score / total_score) * 100 if total_score else 0
                    if percentage >= 80:
                        grade = 'A'
                    elif percentage >= 70:
                        grade = 'B'
                    elif percentage >= 60:
                        grade = 'C'
                    elif percentage >= 50:
                        grade = 'D'
                    else:
                        grade = 'F'
                    
                    # Create or update result
                    try:
                        result, created = Result.objects.update_or_create(
                            student=student,
                            subject=module.name,
                            result_type=result_type,
                            academic_year=academic_year,
                            semester=semester,
                            defaults={
                                'program': program,
                                'department': student.department,
                                'faculty': student.faculty,
                                'score': score,
                                'total_score': total_score,
                                'grade': grade,
                                'uploaded_by': lecturer,
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    except Exception as e:
                        errors.append(f'Row {row_num}: Failed to create/update result: {str(e)}')
                        continue
                    
                    # Create workflow if needed
                    try:
                        hod = HeadOfDepartment.objects.filter(
                            department=student.department,
                            is_active=True
                        ).first()
                        if hod:
                            ResultApprovalWorkflow.objects.update_or_create(
                                result=result,
                                defaults={
                                    'status': 'lecturer_submitted',
                                    'current_hod': hod,
                                }
                            )
                    except Exception as e:
                        errors.append(f'Row {row_num}: Workflow error: {str(e)}')
                
                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')
            
            # Show summary
            if created_count > 0 or updated_count > 0:
                summary = f'Successfully uploaded {created_count} new results'
                if updated_count > 0:
                    summary += f' and updated {updated_count} existing results'
                summary += '. Waiting for HOD approval.'
                messages.success(request, summary)
            
            if errors:
                error_summary = f'Encountered {len(errors)} errors:\n' + '\n'.join(errors[:10])
                if len(errors) > 10:
                    error_summary += f'\n... and {len(errors) - 10} more errors'
                messages.warning(request, error_summary)
            
            if created_count == 0 and updated_count == 0:
                messages.error(request, 'No results were imported. Please check the CSV file and try again.')
                return redirect('upload_results_csv')
            
            return redirect('lecturer_dashboard')
        
        except Exception as e:
            messages.error(request, f'Failed to parse CSV file: {str(e)}')
            return redirect('upload_results_csv')
    
    context = {
        'programs': programs,
        'result_types': result_types,
        'academic_years': academic_years,
        'semesters': semesters,
    }
    return render(request, 'lecturer/upload_results_csv.html', context)


@login_required(login_url='lecturer_login')
def download_csv_template(request):
    """Download a CSV template for result upload"""
    try:
        lecturer = request.user.lecturer_profile
    except:
        return redirect('lecturer_login')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="results_template.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Student_ID', 'Module_Code', 'Score', 'Total_Score'])
    
    # Write example rows
    writer.writerow(['STU001', 'CS101', '45', '100'])
    writer.writerow(['STU002', 'CS101', '78', '100'])
    writer.writerow(['STU003', 'CS102', '92', '100'])
    writer.writerow(['', '', '', ''])  # Empty row for reference
    
    return response


