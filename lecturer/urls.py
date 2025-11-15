from django.urls import path
from . import views

urlpatterns = [
    path('', views.lecturer_home, name='lecturer_home'),
    path('register/', views.lecturer_register, name='lecturer_register'),
    path('login/', views.lecturer_login, name='lecturer_login'),
    path('dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('profile/edit/', views.lecturer_edit_profile, name='lecturer_edit_profile'),
    path('upload-results/', views.upload_results, name='upload_results'),
    path('uploads-by-program/', views.lecturer_uploads_by_program, name='lecturer_uploads_by_program'),
    path('uploads-by-program/<int:program_id>/', views.lecturer_program_results, name='lecturer_program_results'),
    path('results/', views.lecturer_results_list, name='lecturer_results_list'),
    path('student-folders/', views.lecturer_student_folders, name='lecturer_student_folders'),
    path('student-folder/<int:folder_id>/', views.lecturer_folder_detail, name='lecturer_folder_detail'),
    path('result/<int:result_id>/edit/', views.lecturer_edit_result, name='lecturer_edit_result'),
    path('result/<int:result_id>/delete/', views.lecturer_delete_result, name='lecturer_delete_result'),
    path('result/<int:result_id>/submit/', views.lecturer_submit_result, name='lecturer_submit_result'),
    
    # Result Reports
    path('reports/', views.lecturer_reports, name='lecturer_reports'),
    path('reports/create/', views.create_result_report, name='create_result_report'),
    path('reports/<int:report_id>/', views.view_result_report, name='view_result_report'),
    path('reports/<int:report_id>/edit/', views.edit_result_report, name='edit_result_report'),
    path('reports/<int:report_id>/submit/', views.submit_result_report, name='submit_result_report'),
    
    # Submission Deadlines
    path('deadlines/', views.submission_deadlines, name='submission_deadlines'),
    
    path('logout/', views.lecturer_logout, name='lecturer_logout'),
]
