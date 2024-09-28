from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('courses', views.CourseViewSet, basename='course')

courses_router = routers.NestedDefaultRouter(router, 'courses', lookup='course')
courses_router.register('modules', views.ModuleViewSet, basename='course-moduels')

urlpatterns = router.urls + courses_router.urls