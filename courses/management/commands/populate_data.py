from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from courses.models import Assignment, Enrollment, Submission, Module, Course
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with assignments, enrollments, and submissions'

    def handle(self, *args, **kwargs):
        self.populate_assignments()
        self.populate_enrollments()
        self.populate_submissions()

    def populate_assignments(self):
        modules = Module.objects.all()
        for module in modules:
            assignments_data = [
                {'name': 'Assignment 1', 'description': 'First assignment for the module', 'due_date': timezone.now() + timedelta(days=7), 'max_score': 100},
                {'name': 'Assignment 2', 'description': 'Second assignment for the module', 'due_date': timezone.now() + timedelta(days=14), 'max_score': 100},
                {'name': 'Assignment 3', 'description': 'Third assignment for the module', 'due_date': timezone.now() + timedelta(days=21), 'max_score': 100},
            ]
            for assignment_info in assignments_data:
                assignment = Assignment.objects.create(
                    module=module,
                    name=assignment_info['name'],
                    description=assignment_info['description'],
                    due_date=assignment_info['due_date'],
                    max_score=assignment_info['max_score']
                )
                self.stdout.write(self.style.SUCCESS(f"Created Assignment: {assignment.name} for Module: {module.name}"))

    def populate_enrollments(self):
        courses = Course.objects.all()
        students = User.objects.filter(role="ST") 
        for student in students:
            for course in courses:
                enrollment = Enrollment.objects.create(
                    course=course,
                    student=student,
                    progress=0.0,
                    grade=0.0,
                    status=Enrollment.Status.ACTIVE
                )
                self.stdout.write(self.style.SUCCESS(f"Created Enrollment for {student.email} in Course: {course.name}"))

    def populate_submissions(self):
        assignments = Assignment.objects.all()
        students = User.objects.filter(role="ST")  
        for assignment in assignments:
            for student in students:
                submission = Submission.objects.create(
                    assignment=assignment,
                    student=student,
                    feedback="Good job on this submission!",
                    file=None  
                )
                self.stdout.write(self.style.SUCCESS(f"Created Submission for {student.email} for Assignment: {assignment.name}"))
