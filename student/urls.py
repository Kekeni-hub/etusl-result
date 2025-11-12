from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.student_login, name='student_login'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('download-result/<int:result_id>/', views.download_result_pdf, name='download_result'),
    path('logout/', views.student_logout, name='student_logout'),
]
