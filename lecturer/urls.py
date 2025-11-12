from django.urls import path
from . import views

urlpatterns = [
    path('', views.lecturer_home, name='lecturer_home'),
    path('register/', views.lecturer_register, name='lecturer_register'),
    path('login/', views.lecturer_login, name='lecturer_login'),
    path('dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('upload-results/', views.upload_results, name='upload_results'),
    path('logout/', views.lecturer_logout, name='lecturer_logout'),
]
