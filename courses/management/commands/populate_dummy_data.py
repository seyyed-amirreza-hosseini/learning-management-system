import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from courses.models import Student, Teacher, Course, Review, InstructorCourse, Module, Lesson, VideoLecture, Quiz, Question, Choice, QuizSubmission, Assignment, Enrollment, Submission
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with dummy data'

    def create_dummy_users(self, num_students=10, num_teachers=5):
        students = []
        teachers = []
        
        student_names = [
            "Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince", "Ethan Hunt",
            "Fiona Gallagher", "George Costanza", "Hannah Montana", "Ivy League", "Jack Sparrow"
        ]

        teacher_names = [
            "Dr. Emily White", "Prof. John Doe", "Ms. Sarah Connor", "Mr. Bruce Wayne", "Dr. Hermione Granger"
        ]
        
        for i in range(num_students):
            # Use all parts except the last as first name
            name_parts = student_names[i].rsplit(' ', 1)  # Split from the right, keeping the last part as last name
            first_name = name_parts[0]
            last_name = name_parts[1]
            user = User.objects.create_user(
                password='password',
                first_name=first_name,
                last_name=last_name,
                email=f'student{i}@example.com'
            )
            students.append(Student.objects.create(user=user, major=f'Major {random.choice(["Mathematics", "Science", "Arts", "Engineering", "Business"])}'))

        for i in range(num_teachers):
            # Use all parts except the last as first name
            name_parts = teacher_names[i].rsplit(' ', 1)  # Split from the right, keeping the last part as last name
            first_name = name_parts[0]
            last_name = name_parts[1]
            user = User.objects.create_user(
                password='password',
                first_name=first_name,
                last_name=last_name,
                email=f'teacher{i}@example.com'
            )
            teachers.append(Teacher.objects.create(user=user, department=f'Department of {random.choice(["Mathematics", "Science", "Arts", "Engineering", "Business"])}'))
        
        return students, teachers

    def create_dummy_courses(self, teachers, num_courses=10):
        courses = []
        course_names = [
            "Introduction to Programming", "Data Science 101", "Advanced Mathematics",
            "Psychology Basics", "Fundamentals of Design", "Business Management",
            "Digital Marketing", "Artificial Intelligence", "Web Development",
            "Machine Learning"
        ]
        
        for i in range(num_courses):
            course = Course.objects.create(
                name=course_names[i],
                description=f'This course covers the basics of {course_names[i].lower()}.',
                category='Academics',
                level=random.choice([Course.Level.BEGINNER, Course.Level.INTERMEDIATE, Course.Level.ADVANCED]),
                price=random.uniform(100, 500) if random.choice([True, False]) else None
            )
            courses.append(course)

            # Assign a random number of teachers to the course
            for _ in range(random.randint(1, len(teachers))):
                InstructorCourse.objects.create(
                    course=course,
                    instructor=random.choice(teachers),
                    assigned_date=timezone.now() - timedelta(days=random.randint(0, 365)),
                    role=random.choice([InstructorCourse.Role.TEACHER, InstructorCourse.Role.ASSISTANT, InstructorCourse.Role.COORDINATOR])
                )

        return courses

    def create_dummy_reviews(self, students, courses, num_reviews=20):
        for _ in range(num_reviews):
            user_email = random.choice(students)  # Assuming this is an email string
            course = random.choice(courses)

            # Fetch User instance by email
            try:
                user_instance = User.objects.get(email=user_email)  # Adjust based on your User model's email field
            except User.DoesNotExist:
                print(f"User with email {user_email} does not exist.")
                continue  # Skip this iteration if user does not exist

            # Check if review already exists
            if not Review.objects.filter(user=user_instance, course=course).exists():
                # Create your review
                review = Review(user=user_instance, course=course, rating=random.randint(1, 5), comment="Dummy review.")
                review.save()

    def create_dummy_modules(self, courses, num_modules=5):
        for course in courses:
            for i in range(num_modules):
                Module.objects.create(
                    name=f'Module {i + 1} for {course.name}',
                    description=f'Description for Module {i + 1}. This module covers important topics related to {course.name}.',
                    order=i + 1,
                    course=course
                )

    def create_dummy_lessons(self, modules, num_lessons=3):
        for module in modules:
            for i in range(num_lessons):
                Lesson.objects.create(
                    name=f'Lesson {i + 1} for {module.name}',
                    content_type=random.choice([Lesson.ContentType.VIDEO, Lesson.ContentType.ARTICLE]),
                    content='This is some meaningful content for the lesson.',
                    module=module,
                    order=i + 1,
                    duration=timedelta(hours=random.randint(1, 3)),
                    is_published=True,
                    resources=None
                )

    def create_dummy_quizzes(self, lessons, num_quizzes=5):
        for lesson in lessons:
            for i in range(num_quizzes):
                quiz = Quiz.objects.create(
                    lesson=lesson,
                    title=f'Quiz {i + 1} for {lesson.name}',
                    description='This quiz tests your understanding of the lesson material.',
                    passing_score=random.randint(50, 100)
                )

                # Create questions for the quiz
                for j in range(3):  # 3 questions per quiz
                    question = Question.objects.create(
                        quiz=quiz,
                        text=f'Question {j + 1} for {quiz.title}?'
                    )

                    # Create choices for each question
                    for k in range(4):  # 4 choices per question
                        is_correct = k == random.randint(0, 3)  # Randomly assign one correct answer
                        Choice.objects.create(
                            question=question,
                            text=f'Choice {k + 1} for {question.text}',
                            is_correct=is_correct
                        )

    def create_dummy_assignments(self, lessons, num_assignments=2):
        for lesson in lessons:
            for i in range(num_assignments):
                Assignment.objects.create(
                    name=f'Assignment {i + 1} for {lesson.name}',
                    description='This is a sample assignment that helps reinforce your understanding of the material.',
                    due_date=timezone.now() + timedelta(days=random.randint(1, 30)),
                    max_score=random.randint(50, 100),
                    lesson=lesson
                )

    def create_dummy_enrollments(self, students, courses, num_enrollments=15):
        for _ in range(num_enrollments):
            user_email = random.choice(students)
            course = random.choice(courses)

            try:
                user_instance = User.objects.get(email=user_email)
            except User.DoesNotExist:
                print(f"User with email {user_email} does not exist.")
                continue  # Skip if user does not exist

            # Check if the enrollment already exists
            if not Enrollment.objects.filter(user=user_instance, course=course).exists():
                Enrollment.objects.create(user=user_instance, course=course)
            else:
                print(f"Enrollment for user {user_instance.email} in course {course.id} already exists.")

    def handle(self, *args, **options):
        students, teachers = self.create_dummy_users(num_students=10, num_teachers=5)
        courses = self.create_dummy_courses(teachers, num_courses=10)
        self.create_dummy_reviews(students, courses, num_reviews=20)

        modules = Module.objects.all()  # Get all modules to create lessons
        self.create_dummy_modules(courses, num_modules=5)
        lessons = Lesson.objects.all()  # Get all lessons for quizzes and assignments
        self.create_dummy_quizzes(lessons, num_quizzes=2)
        self.create_dummy_assignments(lessons, num_assignments=2)

        self.create_dummy_enrollments(students, courses, num_enrollments=15)

        self.stdout.write(self.style.SUCCESS('Dummy data populated successfully.'))
