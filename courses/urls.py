from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('courses', views.CourseViewSet, basename='course')
router.register('teachers', views.TeacherViewSet, basename='teacher')
router.register('students', views.StudentViewSet, basename='student')
router.register('enrollments', views.EnrollmentViewSet, basename='enrollment')
router.register('assignments', views.AssignmentViewSet, basename='assignment')
router.register('forums', views.ForumViewSet, basename='forum')

courses_router = routers.NestedDefaultRouter(router, 'courses', lookup='course')
courses_router.register('modules', views.ModuleViewSet, basename='course-moduels')
courses_router.register('reviews', views.ReviewViewSet, basename='course-reviews')

modules_router = routers.NestedDefaultRouter(courses_router, 'modules', lookup='module')
modules_router.register('lessons', views.LessonViewSet, basename='module-lessons')

assignment_router = routers.NestedDefaultRouter(router, 'assignments', lookup='assignment')
assignment_router.register('submissions', views.SubmissionViewSet, basename='assignment-submissions')

forum_router = routers.NestedDefaultRouter(router, 'forums', lookup='forum')
forum_router.register('posts', views.PostViewSet, basename='forum-posts')

urlpatterns = router.urls + courses_router.urls + modules_router.urls + assignment_router.urls