from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Student, Teacher, Course, Module, Lesson, Assignment, InstructorCourse, Enrollment, Submission
from datetime import timedelta
from django.utils import timezone  # Correct import for timezone

class Command(BaseCommand):
    help = 'Populate the database with predefined data'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Function to get or create a user
        def get_or_create_user(first_name, last_name, email, password):
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'password': password
                }
            )
            if created:
                user.set_password(password)  # Ensure the password is hashed
                user.save()
            return user

        # Create Teachers
        teachers = []
        teacher_data = [
            {"first_name": "John", "last_name": "Doe", "email": "jdoe@example.com", "department": "Computer Science"},
            {"first_name": "Alice", "last_name": "Smith", "email": "asmith@example.com", "department": "Mathematics"},
            {"first_name": "Bob", "last_name": "White", "email": "bwhite@example.com", "department": "Physics"},
            # Add more teachers as needed
        ]
        for data in teacher_data:
            user = get_or_create_user(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password='password123'
            )
            teacher = Teacher.objects.create(user=user, department=data["department"])
            teachers.append(teacher)

        # Create Students
        students = []
        student_data = [
            {"first_name": "Emily", "last_name": "Brown", "email": "student1@example.com", "major": "Computer Science"},
            {"first_name": "Michael", "last_name": "Johnson", "email": "student2@example.com", "major": "Mathematics"},
            {"first_name": "Sarah", "last_name": "Williams", "email": "student3@example.com", "major": "Physics"},
            # Add more students as needed
        ]
        for data in student_data:
            user = get_or_create_user(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password='password123'
            )
            student = Student.objects.create(user=user, major=data["major"])
            students.append(student)

        # Create Courses
        course_data = [
            {"name": "Introduction to Python", "description": "Learn the basics of Python programming.", "category": "Programming", "level": Course.Level.BEGINNER, "price": 49.99},
            {"name": "Advanced Machine Learning", "description": "Deep dive into machine learning algorithms.", "category": "Data Science", "level": Course.Level.ADVANCED, "price": 199.99},
            {"name": "Web Development with Django", "description": "Build web applications using Django.", "category": "Web Development", "level": Course.Level.INTERMEDIATE, "price": 99.99},
            {"name": "Data Analysis with Pandas", "description": "Analyze data using Pandas library.", "category": "Data Science", "level": Course.Level.INTERMEDIATE, "price": 79.99},
            {"name": "Introduction to Databases", "description": "Learn about relational databases and SQL.", "category": "Database", "level": Course.Level.BEGINNER, "price": 59.99},
            # Add more courses as needed
        ]

        courses = []
        for data in course_data:
            course = Course.objects.create(
                name=data["name"],
                description=data["description"],
                category=data["category"],
                level=data["level"],
                price=data["price"]
            )
            courses.append(course)
            # Assign instructors to courses
            for teacher in teachers[:3]:
                InstructorCourse.objects.create(
                    course=course,
                    instructor=teacher,
                    assigned_date=timezone.now() - timedelta(days=10),
                    role=InstructorCourse.Role.TEACHER
                )

            # Create Modules
            module_data = [
                {"name": "Introduction", "description": "Introduction to the course content and structure."},
                {"name": "Basics", "description": "Basic concepts and foundational knowledge."},
                {"name": "Intermediate Concepts", "description": "Intermediate level topics and applications."},
                {"name": "Advanced Topics", "description": "Advanced topics and in-depth analysis."},
                {"name": "Project", "description": "Course project and practical applications."},
            ]
            for j, mod_data in enumerate(module_data, start=1):
                module = Module.objects.create(
                    name=f'{mod_data["name"]} for {course.name}',
                    description=f'{mod_data["description"]} for {course.name}',
                    order=j,
                    course=course
                )

                # Create Lessons
                lesson_data = [
                    {"name": "Lesson 1", "content_type": Lesson.ContentType.VIDEO, "content": "Video content for lesson 1."},
                    {"name": "Lesson 2", "content_type": Lesson.ContentType.ARTICLE, "content": "Article content for lesson 2."},
                    {"name": "Lesson 3", "content_type": Lesson.ContentType.QUIZ, "content": "Quiz content for lesson 3."},
                    {"name": "Lesson 4", "content_type": Lesson.ContentType.ASSIGNMENT, "content": "Assignment content for lesson 4."},
                    {"name": "Lesson 5", "content_type": Lesson.ContentType.PRESENTATION, "content": "Presentation content for lesson 5."},
                    # Add more lessons as needed
                ]
                for k, les_data in enumerate(lesson_data, start=1):
                    Lesson.objects.create(
                        name=f'{les_data["name"]} for Module {j} of {course.name}',
                        content_type=les_data["content_type"],
                        content=f'{les_data["content"]} for Module {j} of {course.name}',
                        module=module,
                        order=k,
                        duration=timedelta(minutes=30),
                        is_published=True
                    )

        # Create Assignments
        assignments = []
        for i in range(1, 31):
            selected_course = courses[i % len(courses)]
            selected_module = selected_course.modules.first()  # Select first module
            selected_lesson = selected_module.lessons.first()  # Select first lesson
            
            assignment = Assignment.objects.create(
                name=f'Assignment {i}',
                description=f'Description for Assignment {i}',
                due_date=timezone.now() + timedelta(days=i),
                max_score=20,
                course=selected_course,
                module=selected_module,  # Associate with module
                lesson=selected_lesson   # Associate with lesson
            )
            assignments.append(assignment)

        # Create Enrollments
        for student in students:
            for course in courses[:5]:
                Enrollment.objects.create(
                    student=student,
                    course=course
                )

        # Create Submissions
        for assignment in assignments:
            for student in students[:10]:
                Submission.objects.create(
                    assignment=assignment,
                    student=student,
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with predefined data'))
