from django.urls import path
from . import views


urlpatterns = [
    path('', views.course_list),
    path('<int:id>/', views.course_detail),
]
