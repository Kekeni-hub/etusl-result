from django.contrib import admin
from .models import Faculty, Department, Program, Student, Result

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'faculty', 'created_at', 'updated_at')
    list_filter = ('faculty', 'created_at')
    search_fields = ('name', 'code', 'faculty__name')
    ordering = ('name',)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'created_at', 'updated_at')
    list_filter = ('department', 'created_at')
    search_fields = ('name', 'code', 'department__name')
    ordering = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    def photo_tag(self, obj):
        from django.utils.html import format_html
        if obj.photo:
            return format_html('<img src="{}" style="height:40px;border-radius:50%;"/>', obj.photo.url)
        return ''
    photo_tag.short_description = 'Photo'

    list_display = ('photo_tag', 'get_full_name', 'student_id', 'email', 'faculty', 'department', 'current_year', 'is_active')
    list_filter = ('faculty', 'department', 'current_year', 'is_active', 'registration_date')
    search_fields = ('user__first_name', 'user__last_name', 'student_id', 'email')
    readonly_fields = ('registration_date', 'updated_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Information', {'fields': ('student_id', 'email', 'phone', 'date_of_birth', 'address', 'photo')}),
        ('Academic Information', {'fields': ('faculty', 'department', 'program', 'current_year')}),
        ('Status', {'fields': ('is_active',)}),
        ('Dates', {'fields': ('registration_date', 'updated_at')}),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'result_type', 'score', 'grade', 'academic_year', 'is_published')
    list_filter = ('result_type', 'academic_year', 'semester', 'is_published', 'uploaded_date', 'faculty', 'department')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'subject', 'student__student_id')
    readonly_fields = ('uploaded_date', 'updated_date', 'published_date')
    
    fieldsets = (
        ('Student & Subject', {'fields': ('student', 'subject', 'result_type')}),
        ('Scores & Grade', {'fields': ('score', 'total_score', 'grade')}),
        ('Academic Information', {'fields': ('program', 'department', 'faculty', 'academic_year', 'semester')}),
        ('Upload Information', {'fields': ('uploaded_by', 'is_published')}),
        ('Dates', {'fields': ('uploaded_date', 'updated_date', 'published_date')}),
    )

