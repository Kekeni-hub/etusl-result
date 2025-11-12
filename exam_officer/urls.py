from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculties/', views.manage_faculties, name='manage_faculties'),
    path('departments/', views.manage_departments, name='manage_departments'),
    path('results/', views.manage_results, name='manage_results'),
    path('notifications/', views.send_notification, name='send_notification'),
    path('reports/', views.view_reports, name='view_reports'),
    path('logout/', views.admin_logout, name='admin_logout'),
]
