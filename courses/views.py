from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Course
from .serializers import CourseSerializer
from .permissions import IsAdminOrTeacher


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return Course.objects.prefetch_related('instructors').all()