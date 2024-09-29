from rest_framework import serializers
from .models import Course, Teacher, Module, Lesson


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')

    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'department']
    
    def get_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'


class CourseSerializer(serializers.ModelSerializer):
    instructors = TeacherSerializer(many=True, read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'category', 'level', 'price', 'instructors', 'updated_at']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'order', 'updated_at']

    def create(self, validated_data):
        course_id = self.context['course_id']
        return Module.objects.create(course_id=course_id, **validated_data)    


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'content_type', 'content', 'order', 'duration', 'is_published', 'updated_at', 'resources']

    def create(self, validated_data):
        module_id = self.context['module_id']
        return Lesson.objects.create(module_id=module_id, **validated_data) 