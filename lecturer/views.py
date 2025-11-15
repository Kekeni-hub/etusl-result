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
from datetime import datetime
import json

from .models import Lecturer
from .forms import LecturerProfileForm
from student.models import Student, Result, Faculty, Department, Program, Module, Assessment
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
                for entry in payload:
                    student_id = entry.get('student_id')
                    module_code = entry.get('module_code', '').strip()
                    academic_year = entry.get('academic_year')
                    semester = entry.get('semester')
                    assessments = entry.get('assessments', {})

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

                    # After creating assessments for this student+module, recalculate module Result
                    result = Result.objects.filter(student=student, subject=module.name, academic_year=academic_year, semester=semester).first()
                    if result:
                        try:
                            result.recalculate_from_assessments()
                        except Exception:
                            pass
                    else:
                        # If no result exists yet, create one
                        try:
                            result = Result.objects.create(
                                student=student,
                                subject=module.name,
                                program=student.program,
                                department=student.department,
                                faculty=student.faculty,
                                result_type='module',
                                academic_year=academic_year,
                                semester=semester,
                                score=0,
                                total_score=100,
                                grade='F',
                                uploaded_by=lecturer,
                            )
                            try:
                                result.recalculate_from_assessments()
                            except Exception:
                                pass
                        except Exception as e:
                            errors.append(f'Could not create result for {student.student_id} / {module_code}: {e}')

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

