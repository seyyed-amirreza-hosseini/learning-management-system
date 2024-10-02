from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Course, Teacher, Module, Lesson, Student, Enrollment


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')
    user_id = serializers.IntegerField()

    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'user_id', 'department']
    
    def get_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def create(self, validated_data):
        User = get_user_model()
        if not User.objects.filter(pk=validated_data.get('user_id')).exists():
            raise ValidationError("User with the give ID was not found")
        if Teacher.objects.filter(user_id=validated_data.get('user_id')).exists():
            raise ValidationError('This user is already exists')
        return super().create(validated_data)


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')
    user_id = serializers.IntegerField()

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'user_id', 'major']
    
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


class SimpleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'category', 'price']


class SimpleStudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'major']

    def get_full_name(self, student):
        return f'{student.user.first_name} {student.user.last_name}'    


class EnrollmentSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer()
    student = SimpleStudentSerializer()

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'student', 'enrollment_date', 'status']


class EnrollmentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    student_id = serializers.IntegerField()

    def validate_course_id(self, course_id):
        if not Course.objects.filter(id=course_id).exists():
            raise ValidationError('No course with the given ID was found')
        return course_id
    
    def validate_student_id(self, student_id):
        if not Student.objects.filter(id=student_id).exists():
            raise ValidationError('No student with the given ID was found')
        return student_id
    
    def save(self, **kwargs):
        validated_data = self.validated_data.copy()
        
        course_id = validated_data.pop('course_id')
        student_id = validated_data.pop('student_id')

        grade = validated_data.get('grade', 0)

        try:
            enrollment = Enrollment.objects.create(course_id=course_id, student_id=student_id, grade=grade)
            return enrollment
        except IntegrityError:
            raise ValidationError('The student is already enrolled in this course.')