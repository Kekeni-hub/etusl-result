from django.urls import path
from . import views

urlpatterns = [
    path('portal/', views.admin_portal, name='admin_portal'),
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculties/', views.manage_faculties, name='manage_faculties'),
    path('departments/', views.manage_departments, name='manage_departments'),
    path('add-student/', views.officer_add_student, name='officer_add_student'),
    path('add-program/', views.officer_add_program, name='officer_add_program'),
    path('results/', views.manage_results, name='manage_results'),
    path('notifications/', views.send_notification, name='send_notification'),
    path('reports/', views.view_reports, name='view_reports'),
    path('dean-approved-results/', views.manage_dean_approved_results, name='manage_dean_approved_results'),
    path('publish-result/<int:workflow_id>/', views.publish_result, name='publish_result'),
    
    # Result Publishing Notifications
    path('publish-notice/create/', views.create_result_publishing_notice, name='create_result_publishing_notice'),
    path('publish-notice/<int:notice_id>/send/', views.send_result_publishing_notice, name='send_result_publishing_notice'),
    
    # Grade Deadline Notifications
    path('grade-deadline/create/', views.create_grade_deadline_notice, name='create_grade_deadline_notice'),
    path('grade-deadline/<int:notice_id>/send/', views.send_grade_deadline_notice, name='send_grade_deadline_notice'),
    
    path('logout/', views.admin_logout, name='admin_logout'),
]
