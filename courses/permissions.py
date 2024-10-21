from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Course, Enrollment, Student, Teacher


METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        # Make sure that user is not Anonymouse
        if request.user.is_authenticated:
            return bool(
                request.user and
                (request.user.is_staff or request.user.role=='TE')
            )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        if request.method in METHODS:
            if request.user.is_authenticated:
                return bool(
                    request.user and
                    (request.user.is_staff or request.user.role=='TE')
                )


class IsAdminOrOwnTeacher(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        if request.user.is_authenticated:    
            if request.method in METHODS:
                return bool(
                    request.user and
                    (request.user.is_staff or obj.user == request.user) 
                )


class IsAdminOrStudentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        if request.method in METHODS:
            return bool(
                request.user and
                (request.user.is_staff or obj.user == request.user)
            )


class IsStudentAndSubmissionOwner(BasePermission):
    """
    Custom permission to allow students to update or delete only their own submissions
    if they are enrolled in the course related to the assignment.
    """
        
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        if request.user.is_authenticated:
            return bool( 
                request.user and request.user.role == 'ST' 
            )
        else:
            return False
    
    def has_object_permission(self, request, view, obj):
        # Let admin to do everything
        if request.user.is_staff:
            return True
        
        # Ensure the user is authenticated and is a student
        if not (request.user.is_authenticated and request.user.role == 'ST'):
            return False

        # The obj here is the Submission object
        submission = obj  
        student = request.user.student

        # Check if the submission belongs to the student
        if submission.student != student:
            return False
        
        # Check if the student is enrolled in the course related to the assignment
        assignment = submission.assignment
        course = assignment.lesson.module.course
        
        # Ensure the student is enrolled in the course
        is_enrolled = Enrollment.objects.filter(course=course, student=student).exists()

        return is_enrolled


class IsStudentEnrolledOrTeacherInstructor(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        
        elif request.user.is_authenticated:
            course_id = view.kwargs.get('course_pk')
            if not course_id:
                return False
            
            if request.user.role == 'ST':
            
                try:
                    student = Student.objects.get(user_id=request.user.id)
                except Student.DoesNotExist:
                    return False
                is_student_enrolled = Enrollment.objects.filter(
                    course_id=course_id,
                    student_id=student.id
                ).exists()

                return is_student_enrolled
            
            elif request.user.role == 'TE':
                try:
                    teacher = Teacher.objects.get(user_id=request.user.id)
                except Teacher.DoesNotExist:
                    return False
                is_teacher_instructor = Course.objects.filter(
                    id=course_id,
                    instructors=teacher
                ).exists()
                
                return is_teacher_instructor
        else:
            return False


class IsStudentOrTeacherReviewOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True 
        elif request.user.is_authenticated:
            return bool(
                request.user and
                obj.user == request.user 
            )
        else:
            return False


class IsTeacherForumOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'TE' and obj.user == request.user) or request.user.is_staff
        )    
