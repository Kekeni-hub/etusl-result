from django.urls import path
from . import views

urlpatterns = [
    # HOD full paths
    path('hod/login/', views.hod_login, name='hod_login'),
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('hod/review/<int:workflow_id>/', views.hod_review_result, name='hod_review_result'),
    path('hod/logout/', views.hod_logout, name='hod_logout'),
    path('dean/login/', views.dean_login, name='dean_login'),
    path('dean/dashboard/', views.dean_dashboard, name='dean_dashboard'),
    path('dean/add-student/', views.dean_add_student, name='dean_add_student'),
    path('dean/add-program/', views.dean_add_program, name='dean_add_program'),
    path('dean/review/<int:workflow_id>/', views.dean_review_result, name='dean_review_result'),
    path('dean/logout/', views.dean_logout, name='dean_logout'),
]
