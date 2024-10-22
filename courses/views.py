from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied, MethodNotAllowed
from notifications.tasks import send_assignment_reminder_email
from .models import Course, Review, Module, Lesson, Teacher, Student, Enrollment, Assignment, Submission, Forum, Post
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, TeacherSerializer, StudentSerializer, EnrollmentSerializer, EnrollmentCreateSerializer, AssignmentSerializer, AssignmentCreateSerializer, SubmissionSerializer, StudentSubmissionCreateSerializer, AdminSubmissionCreateSerializer, ReviewSerializer, ReviewCreateSerializer, ForumSerializer, PostSerializer
from .permissions import IsAdminOrTeacher, IsAdminOrOwnTeacher, IsAdminOrStudentOwner, IsStudentAndSubmissionOwner, IsStudentEnrolledOrTeacherInstructor, IsStudentOrTeacherReviewOwner, IsTeacherForumOwner, IsStudentOrTeacher, IsPostOwner
from .filters import CourseFilter


User = get_user_model()


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter

    def get_queryset(self):
        return Course.objects \
            .prefetch_related('instructors__user', 'reviews') \
            .all()


class ReviewViewSet(ModelViewSet):
    def get_queryset(self):
        return Review.objects.filter(course_id=self.kwargs['course_pk'])
    
    def get_serializer_context(self):
        return {
            'course_id': self.kwargs['course_pk'],
            'user_id': self.request.user.id,
        }
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method == 'POST':
            return [IsStudentEnrolledOrTeacherInstructor()]
        else:
            return [IsStudentOrTeacherReviewOwner()]


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
    queryset = Teacher.objects.select_related('user').all()
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
                return Student.objects.select_related('user').all()
            elif user.role == 'TE':
                # Ensure we get the teacher instance
                try:
                    teacher = Teacher.objects.get(user_id=user.id)
                except Teacher.DoesNotExist:
                    raise ValidationError("Teacher with the give ID was not found")  # If the teacher is not found, return an empty queryset

                # Return students enrolled in the teacher's courses
                return Student.objects.select_related('user').filter(enrollments__course__instructors=teacher)     
            elif user.role == 'ST':
                return Student.objects.select_related('user').filter(user_id=user.id)
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
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        queryset = Assignment.objects.select_related('lesson__module__course')
        
        if user.is_staff:
            return queryset
        elif user.role == 'TE':
            teacher = Teacher.objects.get(user_id=user.id)
            return queryset.filter(lesson__module__course__instructors__in=[teacher])
        elif user.role == 'ST':
            student = Student.objects.get(user_id=user.id)
            return queryset.filter(lesson__module__course__enrollments__student=student)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssignmentCreateSerializer
        return AssignmentSerializer
    
    def perform_create(self, serializer):
        teacher = Teacher.objects.get(user=self.request.user)
        lesson_id = serializer.validated_data.get('lesson_id')

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            raise ValidationError({'detail': 'Invalid lesson ID.'})

        if teacher not in lesson.module.course.instructors.all():
            raise PermissionDenied('You can only create assignments for your own courses.')
        
        assignment = serializer.save()

        student_emails = User.objects.filter(
            student__enrollments__course=lesson.module.course
        ).values_list('email', flat=True)

        if student_emails:
            subject = f'New Assignment: {assignment.name}'
            message = (
                f'Dear Student,\n\n'
                f'You have a new assignment for the lesson "{lesson.name}" in the course "{lesson.module.course.name}".\n'
                f'Description: {assignment.description}\n'
                f'Due Date: {assignment.due_date}\n\n'
                f'Please make sure to submit your work on time.'
            )
            send_assignment_reminder_email.delay(subject, message, list(student_emails))


class SubmissionViewSet(ModelViewSet):
    permission_classes = [IsStudentAndSubmissionOwner]
    
    def get_queryset(self):
        assignment_id = self.kwargs['assignment_pk']

        return Submission.objects \
            .select_related('student__user') \
            .select_related('assignment__lesson__module__course') \
            .filter(assignment_id=assignment_id) \
            .all()

    def get_serializer_class(self):
        user = self.request.user

        if self.request.method == 'POST':
            if user.is_staff:
                return AdminSubmissionCreateSerializer
            elif user.role == 'ST': 
                return StudentSubmissionCreateSerializer
        return SubmissionSerializer
    
    def get_serializer_context(self):    
        user = self.request.user
        
        if user.role == 'ST':
            student_id = user.student.id
        elif user.is_staff:
            student_id = None
        
        return {
            'assignment_id': self.kwargs['assignment_pk'],
            'student_id': student_id
        }


class ForumViewSet(ModelViewSet):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [IsAdminOrTeacher()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsTeacherForumOwner()]
        elif self.request.method == 'DELETE':
            return [IsAdminUser()]
        
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(forum_id=self.kwargs['forum_pk'])

    def get_serializer_context(self):
        return {'forum_id': self.kwargs['forum_pk']}

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [IsStudentOrTeacher()]
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsPostOwner()]

        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 