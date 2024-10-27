from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg
from django.http import StreamingHttpResponse
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied, MethodNotAllowed
from notifications.tasks import send_assignment_reminder_email
from .models import Course, Review, Module, Lesson, Teacher, Student, Enrollment, Assignment, Submission, Forum, Post, UserCourseProgress, UserActivityLog, Quiz, QuizAttempt
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, TeacherSerializer, StudentSerializer, EnrollmentSerializer, EnrollmentCreateSerializer, AssignmentSerializer, AssignmentCreateSerializer, SubmissionSerializer, StudentSubmissionCreateSerializer, AdminSubmissionCreateSerializer, ReviewSerializer, ReviewCreateSerializer, ForumSerializer, PostSerializer, UserActivityLogSerializer, QuizSerializer, QuizAnswerSerializer, QuizSubmissionSerializer
from .permissions import IsAdminOrTeacher, IsAdminOrOwnTeacher, IsAdminOrStudentOwner, IsStudentAndSubmissionOwner, IsStudentEnrolledOrTeacherInstructor, IsStudentOrTeacherReviewOwner, IsTeacherForumOwner, IsStudentOrTeacher, IsPostOwner
from .filters import CourseFilter
from .utils import log_user_activity
import csv


User = get_user_model()


def generate_csv_report(request):
    rows = UserCourseProgress.objects.all().values_list('user__email', 'course__name', 'progress_percentage')
    response = StreamingHttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="progress_report.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Email', 'Course Name', 'Progress Percentage'])
    for row in rows:
        writer.writerow(row)

    return response

class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter

    def get_queryset(self):
        return Course.objects \
            .prefetch_related('instructors__user', 'reviews') \
            .all()

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()

        log_user_activity(user=request.user, action='view_course', course=course)

        serializer = self.get_serializer(course)
        return Response(serializer.data)
 

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


class AnalyticsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Handle GET requests to the base analytics URL.
        """
        return Response({
            "message": "Welcome to the Analytics API. Use specific endpoints like /completion_rate for data."
        })
    
    @action(detail=True, methods=['get'])
    def course_progress(self, request, pk=None):
        progress = UserCourseProgress.objects.filter(
            user=request.user, course_id=pk
        ).first()
        
        if progress:
            return Response({
                'course_id': int(pk),
                'progress_percentage': progress.progress_percentage,
                'last_accessed': progress.last_accessed                
            })
        
        return Response({"detail": "Progress not found"}, status=404)
    
    @action(detail=True, methods=['get'])
    def completion_rate(self, request, pk=None):
        """
        Calculate and return the average completion rate for a specific course.
        """
        average_progress = UserCourseProgress.objects.filter(course_id=pk).aggregate(avg_progress=Avg('progress_percentage'))

        return Response({'average_completion_rate': average_progress['avg_progress']})
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        logs = UserActivityLog.objects.filter(user=request.user)
        serializer = UserActivityLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def quiz_performance(self, request):
        quiz_attempts = QuizAttempt.objects.filter(user=request.user)
        total_score = quiz_attempts.aggregate(total=Sum('score'))
        return Response({
            'total_score': total_score['total'],
            'attempt_count': quiz_attempts.count(),
        })


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def grade_quiz(self, quiz, user_answers):
        """
        Grades the quiz based on the user's answers.
        """
        correct_answers = quiz.get_correct_answers()
        score = 0

        for user_answer in user_answers:
            question_id = user_answer['question_id']
            selected_option = user_answer['selected_option']
            correct_option = correct_answers.get(question_id)

            if selected_option == correct_option:
                score += 1

        return score
            
    @action(detail=True, methods=['post'])
    def complete_quiz(self, request, pk=None):
        """
        Endpoint for users to complete a quiz.
        """
        quiz = self.get_object()
        user = request.user

        serializer = QuizSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_answers = serializer.validated_data['answers']
        duration = serializer.validated_data.get('duration', None)

        score = self.grade_quiz(quiz, user_answers)
        
        log_user_activity(user=user,
            action='complete quiz', 
            quiz=quiz, 
            details=f'Score: {score}', 
            duration=duration
        )

        quiz_attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            score=score
        )

        return Response({
            "message": "Quiz completed",
            "score": score,
            "attempt_id": quiz_attempt.id},
            status=status.HTTP_200_OK
        )