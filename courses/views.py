from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.prefetch_related('instructors').all()