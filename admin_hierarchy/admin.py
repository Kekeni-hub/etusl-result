from django.contrib import admin
from .models import HeadOfDepartment, DeanOfFaculty, ResultApprovalWorkflow, ApprovalHistory, DeviceToken


@admin.register(HeadOfDepartment)
class HeadOfDepartmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'hod_id', 'department', 'is_active')
    search_fields = ('user__username', 'hod_id', 'email')
    list_filter = ('is_active', 'department')


@admin.register(DeanOfFaculty)
class DeanOfFacultyAdmin(admin.ModelAdmin):
    list_display = ('user', 'dean_id', 'faculty', 'is_active')
    search_fields = ('user__username', 'dean_id', 'email')
    list_filter = ('is_active', 'faculty')


@admin.register(ResultApprovalWorkflow)
class ResultApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ('result', 'status', 'current_hod', 'current_dean')
    search_fields = ('result__student__user__username', 'status')
    list_filter = ('status', 'lecturer_submitted_at')
    readonly_fields = ('lecturer_submitted_at', 'hod_reviewed_at', 'dean_reviewed_at', 'exam_reviewed_at')


@admin.register(ApprovalHistory)
class ApprovalHistoryAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'action', 'admin_user', 'created_at')
    search_fields = ('workflow__result__student__user__username', 'admin_user__username')
    list_filter = ('action', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at', 'updated_at')
