#!/usr/bin/env python
"""
Quick test to verify the new views and URL routes are properly configured.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Etu_student_result.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.urls import reverse, resolve
from lecturer.views import student_performance_view, course_management, export_class_list

def test_views():
    """Test that all views are importable and functioning."""
    print("✓ Views imported successfully")
    
    # Check that views are callable
    assert callable(student_performance_view), "student_performance_view not callable"
    assert callable(course_management), "course_management not callable"
    assert callable(export_class_list), "export_class_list not callable"
    print("✓ All views are callable")

def test_urls():
    """Test that URL routes are properly registered."""
    try:
        url1 = reverse('student_performance_view')
        print(f"✓ student_performance_view URL: {url1}")
        
        url2 = reverse('course_management')
        print(f"✓ course_management URL: {url2}")
        
        # Test export URL with a course ID
        url3 = reverse('export_class_list', args=[1])
        print(f"✓ export_class_list URL: {url3}")
        
    except Exception as e:
        print(f"✗ URL routing error: {e}")
        return False
    
    return True

def test_resolves():
    """Test that URLs resolve to the correct views."""
    try:
        match = resolve('/lecturer/student-performance/')
        assert match.func == student_performance_view, "Student performance view not matched"
        print(f"✓ /lecturer/student-performance/ resolves to student_performance_view")
        
        match = resolve('/lecturer/course-management/')
        assert match.func == course_management, "Course management view not matched"
        print(f"✓ /lecturer/course-management/ resolves to course_management")
        
        match = resolve('/lecturer/course/1/export-class-list/')
        assert match.func == export_class_list, "Export class list view not matched"
        print(f"✓ /lecturer/course/<int:course_id>/export-class-list/ resolves to export_class_list")
        
    except Exception as e:
        print(f"✗ URL resolution error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("Testing new Student Performance and Course Management features...\n")
    
    try:
        test_views()
        print()
        if test_urls():
            print()
            if test_resolves():
                print("\n✓ All tests passed! The new features are properly configured.")
            else:
                print("\n✗ Some URL resolution tests failed.")
                sys.exit(1)
        else:
            print("\n✗ Some URL tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
