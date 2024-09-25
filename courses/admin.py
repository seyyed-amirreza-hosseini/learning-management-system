from django.contrib import admin
from .models import Student, Teacher, Course, Module, Lesson, Enrollment, Assignment, Submission, InstructorCourse


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'price', 'get_instructors', 'updated_at']
    list_filter = ['category', 'level', 'price', 'updated_at']
    list_editable = ['price']

    def get_instructors(self, obj):
        return "\n".join([ins.username for ins in obj.instructors.all()])

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'order', 'updated_at']
    list_filter = ['course', 'order', 'updated_at']


@admin.register(InstructorCourse)
class InstructorCourseAdmin(admin.ModelAdmin):
    list_display = ['course', 'instructor', 'assigned_date', 'role']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'major', 'enrollment_date']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'hire_date']
