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
from student.views import home
from admin_hierarchy.views import hod_index, dean_index

urlpatterns = [
    path('', home, name='home'),
    # Django admin enabled again per user request.
    path('admin/', admin.site.urls),
    path('student/', include('student.urls')),
    path('lecturer/', include('lecturer.urls')),
    path('officer/', include('exam_officer.urls')),
    path('admin-hierarchy/', include('admin_hierarchy.urls')),
    # Direct shortcuts for HOD and DEAN
    path('hod/', hod_index, name='hod_redirect'),
    path('dean/', dean_index, name='dean_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

