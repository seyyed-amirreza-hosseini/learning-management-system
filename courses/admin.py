from django.contrib import admin
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse
from .models import Forum, Student, Teacher, Course, Review, Module, Lesson, Enrollment, Assignment, Submission, InstructorCourse


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'price', 'get_instructors', 'updated_at', 'modules_count']
    list_filter = ['category', 'level', 'price', 'updated_at']
    list_editable = ['price']
    list_per_page = 10
    search_fields = ['name__istartswith']

    @admin.display(description='Instructors')
    def get_instructors(self, obj):
        return ", ".join([str(ins) for ins in obj.instructors.all()])
    
    @admin.display(ordering='modules_count')
    def modules_count(self, course):
        url = (
            reverse('admin:courses_module_changelist')
            + "?"
            + urlencode({
                'course__id': str(course.id)
            }))
        return format_html('<a href="{}">{}</a>', url, course.modules_count)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('instructors__user').annotate(modules_count=Count('modules'))


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'comment', 'rating', 'created_at']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'order', 'updated_at', 'lessons_count']
    list_filter = ['course', 'order', 'updated_at']
    list_per_page = 10
    search_fields = ['name__istartswith']
    autocomplete_fields = ['course']

    @admin.display(ordering='lessons_count')
    def lessons_count(self, module):
        url = (
            reverse('admin:courses_lesson_changelist')
            + "?"
            + urlencode({
                'module__id': str(module.id)
            }))
        return format_html('<a href="{}">{}</a>', url, module.lessons_count)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('order').annotate(lessons_count=Count('lessons'))


@admin.register(InstructorCourse)
class InstructorCourseAdmin(admin.ModelAdmin):
    list_display = ['course', 'instructor', 'assigned_date', 'role']
    list_per_page = 10
    autocomplete_fields = ['course', 'instructor']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'major', 'enrollment_date']
    list_per_page = 10
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']
    autocomplete_fields = ['user']

    def full_name(self, student):
        return f'{student.user.first_name} {student.user.last_name}'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'department', 'hire_date']
    list_per_page = 10
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']
    autocomplete_fields = ['user']

    def full_name(self, teacher):
        return f'{teacher.user.first_name} {teacher.user.last_name}'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type', 'duration', 'module']
    list_per_page = 10
    search_fields = ['name__istartswith']
    autocomplete_fields = ['module']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'student', 'enrollment_date']
    list_per_page = 10
    autocomplete_fields = ['course', 'student']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'due_date', 'lesson']
    list_per_page = 10
    search_fields = ['name']
    autocomplete_fields = ['lesson']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at']
    list_per_page = 10
    autocomplete_fields = ['assignment', 'student']


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'course', 'user']
