from django.contrib import admin
from .models import Lecturer

@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'lecturer_id', 'email', 'faculty', 'department', 'is_verified', 'is_active')
    list_filter = ('faculty', 'department', 'is_verified', 'is_active', 'registration_date')
    search_fields = ('user__first_name', 'user__last_name', 'lecturer_id', 'email')
    readonly_fields = ('registration_date', 'updated_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Information', {'fields': ('lecturer_id', 'email', 'phone')}),
        ('Academic Information', {'fields': ('faculty', 'department', 'specialization')}),
        ('Office Information', {'fields': ('office_location', 'bio')}),
        ('Status', {'fields': ('is_verified', 'is_active')}),
        ('Dates', {'fields': ('registration_date', 'updated_at')}),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

