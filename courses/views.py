from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ValidationError, PermissionDenied, MethodNotAllowed
from .models import Course, Module, Lesson, Teacher, Student, Enrollment, Assignment
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, TeacherSerializer, StudentSerializer, EnrollmentSerializer, EnrollmentCreateSerializer, AssignmentSerializer
from .permissions import IsAdminOrTeacher, IsAdminOrOwnTeacher, IsAdminOrStudentOwner, IsAdminOrTeacherOrStudent


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return Course.objects.prefetch_related('instructors__user').all()
    

class ModuleViewSet(ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return Module.objects.filter(course=self.kwargs['course_pk']).order_by('order')

    def get_serializer_context(self):
        return {'course_id': self.kwargs['course_pk']}


class LessonViewSet(ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return Lesson.objects.filter(module=self.kwargs['module_pk']).order_by('order')

    def get_serializer_context(self):
        return {'module_id': self.kwargs['module_pk']}
    

class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        else:
            return[IsAdminOrOwnTeacher()]


class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            if user.is_staff:
                return Student.objects.all()
            elif user.role == 'TE':
                # Ensure we get the teacher instance
                try:
                    teacher = Teacher.objects.get(user_id=user.id)
                except Teacher.DoesNotExist:
                    raise ValidationError("Teacher with the give ID was not found")  # If the teacher is not found, return an empty queryset

                # Return students enrolled in the teacher's courses
                return Student.objects.filter(enrollments__course__instructors=teacher)     
            elif user.role == 'ST':
                return Student.objects.filter(id=user.id)
        else:
            raise PermissionDenied("Method \"GET\" not allowed.") 
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrTeacher()]
        elif self.request.method == 'POST':
            return [IsAdminUser()]
        else:
            return [IsAdminOrStudentOwner()]


class EnrollmentViewSet(ModelViewSet):

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            if user.is_staff:
                return Enrollment.objects.select_related('student__user').prefetch_related('course__instructors__user').all()
            elif user.role == 'TE':
                raise MethodNotAllowed(self.request.method, detail="GET method is not allowed for teachers.")

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EnrollmentCreateSerializer
        return EnrollmentSerializer
    
    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrTeacher()]
        else:
            return [IsAdminUser()]
        

class AssignmentViewSet(ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrTeacherOrStudent]

    def get_queryset(self):
        user = self.request.user
        queryset = Assignment.objects \
                    .select_related('course') \
                    .select_related('module') \
                    .select_related('lesson') \
                    .all()

        if user.is_authenticated:
            if user.is_staff:
                return queryset
            elif user.role == 'ST':
                return queryset.filter(course__enrollments__student__user=user)
            elif user.role == 'TE':
                teacher = Teacher.objects.get(user=user)
                return queryset.filter(course__instructors__in=[teacher])
        
        raise MethodNotAllowed(self.request.method)
