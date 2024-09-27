from rest_framework import serializers
from .models import Course, Teacher


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')

    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'department']
    
    def get_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'


class CourseSerializer(serializers.ModelSerializer):
    instructors = TeacherSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'category', 'level', 'price', 'instructors']
