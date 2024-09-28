from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from .models import Course, Module, Lesson
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer
from .permissions import IsAdminOrTeacher


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return Course.objects.prefetch_related('instructors').all()
    

class ModuleViewSet(ModelViewSet):
    serializer_class = ModuleSerializer

    def get_queryset(self):
        return Module.objects.filter(course=self.kwargs['course_pk'])

    def get_serializer_context(self):
        return {'course_id': self.kwargs['course_pk']}


class LessonViewSet(ModelViewSet):
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(module=self.kwargs['module_pk'])

    def get_serializer_context(self):
        return {'module_id': self.kwargs['module_pk']}