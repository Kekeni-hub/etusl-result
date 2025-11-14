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
    path('logout/', views.admin_logout, name='admin_logout'),
]
