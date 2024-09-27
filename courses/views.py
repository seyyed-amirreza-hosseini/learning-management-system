from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view()
def course_list(request):
    return Response('ok')


@api_view()
def course_detail(request, id):
    return Response(id)
