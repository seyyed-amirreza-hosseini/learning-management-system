from django.contrib import admin
from .models import Course, Module, Lesson, Enrollment, Assignment, Submission, InstructorCourse


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
