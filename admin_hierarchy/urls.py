from django.urls import path
from . import views

urlpatterns = [
    # HOD full paths
    path('hod/login/', views.hod_login, name='hod_login'),
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    # HOD list pages
    path('hod/pending/', views.hod_pending_list, name='hod_pending_list'),
    path('hod/approved/', views.hod_approved_list, name='hod_approved_list'),
    path('hod/review/<int:workflow_id>/', views.hod_review_result, name='hod_review_result'),
    path('hod/student-folders/', views.hod_student_folders, name='hod_student_folders'),
    path('hod/student-folder/<int:folder_id>/', views.hod_folder_detail, name='hod_folder_detail'),
    
    # HOD Result Overviews and Reports
    path('hod/overviews/', views.hod_result_overviews, name='hod_result_overviews'),
    path('hod/overviews/create/', views.hod_create_overview, name='hod_create_overview'),
    path('hod/overviews/<int:overview_id>/', views.hod_view_overview, name='hod_view_overview'),
    path('hod/overviews/<int:overview_id>/publish/', views.hod_publish_overview, name='hod_publish_overview'),
    path('hod/reports/', views.hod_lecturer_reports, name='hod_lecturer_reports'),
    path('hod/reports/<int:report_id>/', views.hod_review_lecturer_report, name='hod_review_lecturer_report'),
    
    path('hod/logout/', views.hod_logout, name='hod_logout'),
    
    # DEAN full paths
    path('dean/login/', views.dean_login, name='dean_login'),
    path('dean/dashboard/', views.dean_dashboard, name='dean_dashboard'),
    # DEAN list pages
    path('dean/pending/', views.dean_pending_list, name='dean_pending_list'),
    path('dean/finalized/', views.dean_finalized_list, name='dean_finalized_list'),
    path('dean/add-student/', views.dean_add_student, name='dean_add_student'),
    path('dean/add-student/success/', views.dean_add_student_success, name='dean_add_student_success'),
    path('dean/register-student/', views.dean_register_student, name='dean_register_student'),
    path('dean/register-student/success/', views.dean_register_student_success, name='dean_register_student_success'),
    path('dean/add-program/', views.dean_add_program, name='dean_add_program'),
    path('dean/student-folders/', views.dean_student_folders, name='dean_student_folders'),
    path('dean/student-folder/<int:folder_id>/', views.dean_folder_detail, name='dean_folder_detail'),
    
    # DEAN Result Overviews
    path('dean/overviews/', views.dean_result_overviews, name='dean_result_overviews'),
    path('dean/overviews/create/', views.dean_create_overview, name='dean_create_overview'),
    path('dean/overviews/<int:overview_id>/', views.dean_view_overview, name='dean_view_overview'),
    path('dean/overviews/<int:overview_id>/publish/', views.dean_publish_overview, name='dean_publish_overview'),
    
    path('faculties/', views.faculties_list, name='faculties_list'),
    path('faculty/<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),
    path('department/<int:dept_id>/', views.department_detail, name='department_detail'),
    path('dean/review/<int:workflow_id>/', views.dean_review_result, name='dean_review_result'),
    path('dean/logout/', views.dean_logout, name='dean_logout'),
    # Exam Officer preview and publish
    path('exam-officer/preview/', views.exam_officer_preview_results, name='exam_officer_preview_results'),
    path('exam-officer/publish/<int:workflow_id>/', views.exam_officer_publish_result, name='exam_officer_publish_result'),
    # CSV export and archive endpoints
    path('export-results/', views.export_results_csv, name='export_results_csv'),
    path('archive-results/', views.archive_program_results, name='archive_program_results'),
]
