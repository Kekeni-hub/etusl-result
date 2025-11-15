"""
URL patterns for all 15 enhanced features
"""

from django.urls import path
from student import views_enhanced

urlpatterns = [
    # ==================== 1. ANALYTICS & REPORTING ====================
    path('analytics/dashboard/', views_enhanced.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/class-performance/', views_enhanced.class_performance_view, name='class_performance'),
    path('analytics/generate-report/', views_enhanced.generate_analytics_report, name='generate_analytics_report'),
    path('analytics/report/<int:report_id>/', views_enhanced.view_analytics_report, name='view_analytics_report'),
    path('analytics/report/<int:report_id>/export-csv/', views_enhanced.export_analytics_csv, name='export_analytics_csv'),
    
    # ==================== 2. GPA SYSTEM ====================
    path('gpa/cumulative/', views_enhanced.cumulative_gpa_view, name='cumulative_gpa'),
    path('gpa/progress/', views_enhanced.gpa_progress_view, name='gpa_progress'),
    path('gpa/academic-standing/', views_enhanced.academic_standing_view, name='academic_standing'),
    
    # ==================== 3. TRANSCRIPT MANAGEMENT ====================
    path('transcript/request/', views_enhanced.request_transcript, name='request_transcript'),
    path('transcript/my-transcripts/', views_enhanced.my_transcripts, name='my_transcripts'),
    path('transcript/download/<int:transcript_id>/', views_enhanced.download_transcript, name='download_transcript'),
    path('transcript/manage-requests/', views_enhanced.manage_transcript_requests, name='manage_transcript_requests'),
    
    # ==================== 4. ACADEMIC ADVISEMENT ====================
    path('advisement/program-requirements/', views_enhanced.program_requirements_view, name='program_requirements'),
    path('advisement/graduation-checklist/', views_enhanced.graduation_checklist, name='graduation_checklist'),
    path('advisement/advisor-notes/', views_enhanced.advisor_notes_view, name='advisor_notes'),
    
    # ==================== 5. NOTIFICATIONS ====================
    path('notifications/my-notifications/', views_enhanced.my_notifications, name='my_notifications'),
    path('notifications/schedule/', views_enhanced.schedule_notification, name='schedule_notification'),
    
    # ==================== 6. SEARCH & FILTERING ====================
    path('search/advanced/', views_enhanced.advanced_search, name='advanced_search'),
    path('search/saved/', views_enhanced.saved_searches, name='saved_searches'),
    
    # ==================== 7. PROBATION & INTERVENTION ====================
    path('probation/status/', views_enhanced.academic_probation_view, name='probation_status'),
    path('probation/early-warnings/', views_enhanced.early_warnings_view, name='early_warnings'),
    
    # ==================== 8-10. COURSES & CALENDAR ====================
    path('courses/my-enrollments/', views_enhanced.course_enrollments, name='course_enrollments'),
    path('courses/attendance/', views_enhanced.class_attendance_view, name='class_attendance'),
    path('assignments/my-assignments/', views_enhanced.my_assignments, name='my_assignments'),
    path('calendar/academic-calendar/', views_enhanced.academic_calendar_view, name='academic_calendar'),
    
    # ==================== 11. PARENT/GUARDIAN PORTAL ====================
    path('parent/student-results/', views_enhanced.parent_student_results, name='parent_student_results'),
    
    # ==================== 12. DATA INTEGRITY ====================
    path('admin/data-integrity/', views_enhanced.data_integrity_report, name='data_integrity_report'),
]
