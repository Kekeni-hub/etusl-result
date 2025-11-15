"""
URL configuration for Etu_student_result project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from student.views import home, developers
from admin_hierarchy.views import hod_index, dean_index
import admin_hierarchy.views
from rest_framework import routers
from student.api.views import StudentViewSet, ResultViewSet, TokenRotateView
from rest_framework.authtoken import views as drf_auth_views
from .firebase_views import FirebaseVerifyView
from admin_hierarchy.api_views import DeviceTokenView
from student.serializers_enhanced import (
    CumulativeGPAViewSet,
    TranscriptViewSet,
    StudentProgressTrackerViewSet,
    StudentNotificationViewSet,
    GradeDistributionViewSet,
    ClassPerformanceViewSet,
    CourseOfferingViewSet,
    StudentEnrollmentViewSet,
    AssignmentViewSet,
    AssignmentSubmissionViewSet,
)

# API router
router = routers.DefaultRouter()
router.register(r'students', StudentViewSet, basename='api-students')
router.register(r'results', ResultViewSet, basename='api-results')
# Enhanced feature endpoints
router.register(r'gpa', CumulativeGPAViewSet, basename='api-gpa')
router.register(r'transcripts', TranscriptViewSet, basename='api-transcripts')
router.register(r'progress', StudentProgressTrackerViewSet, basename='api-progress')
router.register(r'notifications', StudentNotificationViewSet, basename='api-notifications')
router.register(r'grade-distribution', GradeDistributionViewSet, basename='api-grade-distribution')
router.register(r'class-performance', ClassPerformanceViewSet, basename='api-class-performance')
router.register(r'course-offerings', CourseOfferingViewSet, basename='api-course-offerings')
router.register(r'enrollments', StudentEnrollmentViewSet, basename='api-enrollments')
router.register(r'assignments', AssignmentViewSet, basename='api-assignments')
router.register(r'assignment-submissions', AssignmentSubmissionViewSet, basename='api-assignment-submissions')

urlpatterns = [
    path('', home, name='home'),
    path('developers/', developers, name='developers'),
    # Django admin enabled again per user request.
    path('admin/', admin.site.urls),
    path('student/', include('student.urls')),
    path('student/enhanced/', include('student.urls_enhanced')),
    path('lecturer/', include('lecturer.urls')),
    path('officer/', include('exam_officer.urls')),
    # Direct URL mappings for HOD and DEAN (replacing admin-hierarchy/ include)
    # All dean/hod routes are now at root level for direct access
    path('dean/login/', admin_hierarchy.views.dean_login, name='dean_login'),
    path('dean/dashboard/', admin_hierarchy.views.dean_dashboard, name='dean_dashboard'),
    path('dean/pending/', admin_hierarchy.views.dean_pending_list, name='dean_pending_list'),
    path('dean/finalized/', admin_hierarchy.views.dean_finalized_list, name='dean_finalized_list'),
    path('dean/add-student/', admin_hierarchy.views.dean_add_student, name='dean_add_student'),
    path('dean/add-student/success/', admin_hierarchy.views.dean_add_student_success, name='dean_add_student_success'),
    path('dean/register-student/', admin_hierarchy.views.dean_register_student, name='dean_register_student'),
    path('dean/register-student/success/', admin_hierarchy.views.dean_register_student_success, name='dean_register_student_success'),
    path('dean/add-program/', admin_hierarchy.views.dean_add_program, name='dean_add_program'),
    path('dean/student-folders/', admin_hierarchy.views.dean_student_folders, name='dean_student_folders'),
    path('dean/student-folder/<int:folder_id>/', admin_hierarchy.views.dean_folder_detail, name='dean_folder_detail'),
    path('dean/overviews/', admin_hierarchy.views.dean_result_overviews, name='dean_result_overviews'),
    path('dean/overviews/create/', admin_hierarchy.views.dean_create_overview, name='dean_create_overview'),
    path('dean/overviews/<int:overview_id>/', admin_hierarchy.views.dean_view_overview, name='dean_view_overview'),
    path('dean/overviews/<int:overview_id>/publish/', admin_hierarchy.views.dean_publish_overview, name='dean_publish_overview'),
    path('dean/review/<int:workflow_id>/', admin_hierarchy.views.dean_review_result, name='dean_review_result'),
    path('dean/logout/', admin_hierarchy.views.dean_logout, name='dean_logout'),
    
    path('hod/login/', admin_hierarchy.views.hod_login, name='hod_login'),
    path('hod/dashboard/', admin_hierarchy.views.hod_dashboard, name='hod_dashboard'),
    path('hod/pending/', admin_hierarchy.views.hod_pending_list, name='hod_pending_list'),
    path('hod/approved/', admin_hierarchy.views.hod_approved_list, name='hod_approved_list'),
    path('hod/review/<int:workflow_id>/', admin_hierarchy.views.hod_review_result, name='hod_review_result'),
    path('hod/student-folders/', admin_hierarchy.views.hod_student_folders, name='hod_student_folders'),
    path('hod/student-folder/<int:folder_id>/', admin_hierarchy.views.hod_folder_detail, name='hod_folder_detail'),
    path('hod/overviews/', admin_hierarchy.views.hod_result_overviews, name='hod_result_overviews'),
    path('hod/overviews/create/', admin_hierarchy.views.hod_create_overview, name='hod_create_overview'),
    path('hod/overviews/<int:overview_id>/', admin_hierarchy.views.hod_view_overview, name='hod_view_overview'),
    path('hod/overviews/<int:overview_id>/publish/', admin_hierarchy.views.hod_publish_overview, name='hod_publish_overview'),
    path('hod/reports/', admin_hierarchy.views.hod_lecturer_reports, name='hod_lecturer_reports'),
    path('hod/reports/<int:report_id>/', admin_hierarchy.views.hod_review_lecturer_report, name='hod_review_lecturer_report'),
    path('hod/logout/', admin_hierarchy.views.hod_logout, name='hod_logout'),
    
    # Exam officer and other admin_hierarchy routes (without dean/hod prefix)
    path('faculties/', admin_hierarchy.views.faculties_list, name='faculties_list'),
    path('faculty/<int:faculty_id>/', admin_hierarchy.views.faculty_detail, name='faculty_detail'),
    path('department/<int:dept_id>/', admin_hierarchy.views.department_detail, name='department_detail'),
    path('exam-officer/preview/', admin_hierarchy.views.exam_officer_preview_results, name='exam_officer_preview_results'),
    path('exam-officer/publish/<int:workflow_id>/', admin_hierarchy.views.exam_officer_publish_result, name='exam_officer_publish_result'),
    path('export-results/', admin_hierarchy.views.export_results_csv, name='export_results_csv'),
    path('archive-results/', admin_hierarchy.views.archive_program_results, name='archive_program_results'),
    
    # API
    path('api/', include(router.urls)),
    path('api-token-auth/', drf_auth_views.obtain_auth_token, name='api_token_auth'),
    path('api/token-rotate/', TokenRotateView.as_view(), name='api_token_rotate'),
    # Firebase endpoints
    path('firebase/verify-token/', FirebaseVerifyView.as_view(), name='firebase_verify_token'),
    path('api/device-tokens/', DeviceTokenView.as_view(), name='device-tokens'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

