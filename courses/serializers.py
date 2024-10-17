from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Course, Review, Teacher, Module, Lesson, Student, Enrollment, Assignment, Submission


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
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'category', 'level', 'price', 'average_rating', 'instructors', 'updated_at']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()

        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 2)
            
        return 0


class ReviewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')

    class Meta:
        model = Review
        fields = ['id', 'full_name', 'comment', 'rating']

    def get_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'comment', 'rating']


    def create(self, validated_data):
        course_id = self.context['course_id']
        user_id = self.context['user_id']
        
        try:
            return Review.objects.create(course_id=course_id, user_id=user_id, **validated_data)
        except IntegrityError:
            raise ValidationError({"detail": "You have already submitted a review for this course."})


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
        user = self.context['user']
        
        if Course.objects.filter(id=course_id).exists():
            if user.is_staff:
                return course_id
            
            if user.role == 'TE':
                if Course.objects.filter(id=course_id, instructors__user=user).exists():
                    return course_id
                else:
                    raise ValidationError('You can only enroll students in your own courses.')
        else:
            raise ValidationError('No course with the given ID was found')
        
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


class SimpleModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name']


class SimpleLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'name']


class AssignmentSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField(method_name='get_course_name')
    module_name = serializers.SerializerMethodField(method_name='get_module_name')
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'name', 'description', 'due_date', 'course_name', 'module_name', 'lesson']

    def get_course_name(self, obj):
        return obj.lesson.module.course.name
    
    def get_module_name(self, obj):
        return obj.lesson.module.name
    

class AssignmentCreateSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField()

    class Meta:
        model = Assignment
        fields = ['id', 'name', 'description', 'due_date', 'lesson_id']

    def create(self, validated_data):
        lesson_id = validated_data.pop('lesson_id')

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            raise serializers.ValidationError({"lesson_id": "Invalide lesson ID."})
        
        assignment = Assignment.objects.create(lesson_id=lesson.id, **validated_data)
        return assignment
    

class SubmissionSerializer(serializers.ModelSerializer):
    student = SimpleStudentSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'student', 'submitted_at', 'updated_at', 'file']


class StudentSubmissionCreateSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'student_id', 'file']

    def create(self, validated_data):
        assignment_id = self.context['assignment_id']
        student_id = self.context['student_id']

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Invalide student ID."})
        
        try:
            submission = Submission.objects.create(
                assignment_id=assignment_id,
                student=student,
                **validated_data
            )
        except IntegrityError:
            raise serializers.ValidationError("You have already submitted this assignment.")
        
        return submission


class AdminSubmissionCreateSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField()

    class Meta:
        model = Submission
        fields = ['id', 'student_id', 'file']

    def create(self, validated_data):
        assignment_id = self.context['assignment_id']
        student_id = self.validated_data['student_id']

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Invalide student ID."})
        
        try:
            submission = Submission.objects.create(
                assignment_id=assignment_id,
                student=student,
                **validated_data
            )
        except IntegrityError:
            raise serializers.ValidationError("You have already submitted this assignment.")
        
        return submission