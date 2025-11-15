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
    path('hod/logout/', views.hod_logout, name='hod_logout'),
    path('dean/login/', views.dean_login, name='dean_login'),
    path('dean/dashboard/', views.dean_dashboard, name='dean_dashboard'),
    # DEAN list pages
    path('dean/pending/', views.dean_pending_list, name='dean_pending_list'),
    path('dean/finalized/', views.dean_finalized_list, name='dean_finalized_list'),
    path('dean/add-student/', views.dean_add_student, name='dean_add_student'),
    path('dean/add-program/', views.dean_add_program, name='dean_add_program'),
    path('dean/student-folders/', views.dean_student_folders, name='dean_student_folders'),
    path('dean/student-folder/<int:folder_id>/', views.dean_folder_detail, name='dean_folder_detail'),
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
