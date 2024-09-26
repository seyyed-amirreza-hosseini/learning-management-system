from django.core.management.base import BaseCommand
from datetime import timedelta
from courses.models import Course, Module, Lesson


class Command(BaseCommand):
    help = 'Generate modules and lessons for each course in the database'

    def handle(self, *args, **kwargs):
        courses = Course.objects.all()

        for course in courses:
            if course.name == 'Python 101':
                module_data = [
                    {'name': 'Introduction to Python', 'description': 'Overview of Python and its features', 'order': 1},
                    {'name': 'Python Basics', 'description': 'Basic Python concepts such as variables and data types', 'order': 2},
                    {'name': 'Python Data Types', 'description': 'Understanding Python data types in depth', 'order': 3},
                ]
                lesson_data = [
                    [
                        {'name': 'What is Python?', 'content_type': 'article', 'content': 'Introduction to Python programming language.', 'order': 1, 'duration': timedelta(minutes=10), 'is_published': True},
                        {'name': 'Installing Python', 'content_type': 'video', 'content': 'How to install Python on your machine.', 'order': 2, 'duration': timedelta(minutes=15), 'is_published': True},
                        {'name': 'Hello World!', 'content_type': 'article', 'content': 'Your first Python program.', 'order': 3, 'duration': timedelta(minutes=5), 'is_published': True},
                    ],
                    [
                        {'name': 'Variables in Python', 'content_type': 'article', 'content': 'Learning about variables in Python.', 'order': 1, 'duration': timedelta(minutes=8), 'is_published': True},
                        {'name': 'Control Flow', 'content_type': 'video', 'content': 'How to use control flow in Python.', 'order': 2, 'duration': timedelta(minutes=20), 'is_published': True},
                        {'name': 'Functions in Python', 'content_type': 'article', 'content': 'Introduction to functions in Python.', 'order': 3, 'duration': timedelta(minutes=12), 'is_published': True},
                    ],
                    [
                        {'name': 'Lists, Tuples, and Sets', 'content_type': 'article', 'content': 'Understanding lists, tuples, and sets in Python.', 'order': 1, 'duration': timedelta(minutes=10), 'is_published': True},
                        {'name': 'Dictionaries', 'content_type': 'article', 'content': 'How to work with dictionaries in Python.', 'order': 2, 'duration': timedelta(minutes=10), 'is_published': True},
                        {'name': 'Working with Strings', 'content_type': 'video', 'content': 'Manipulating strings in Python.', 'order': 3, 'duration': timedelta(minutes=18), 'is_published': True},
                    ]
                ]
            elif course.name == 'Advanced Calculus':
                module_data = [
                    {'name': 'Limits and Continuity', 'description': 'Introduction to limits and continuity in calculus', 'order': 1},
                    {'name': 'Differentiation Techniques', 'description': 'Advanced techniques in differentiation', 'order': 2},
                    {'name': 'Integrals', 'description': 'Understanding integrals in calculus', 'order': 3},
                ]
                lesson_data = [
                    [
                        {'name': 'Introduction to Limits', 'content_type': 'video', 'content': 'Introduction to the concept of limits.', 'order': 1, 'duration': timedelta(minutes=12), 'is_published': True},
                        {'name': 'Continuity and Discontinuity', 'content_type': 'article', 'content': 'Understanding continuous and discontinuous functions.', 'order': 2, 'duration': timedelta(minutes=10), 'is_published': True},
                        {'name': 'Theorems on Limits', 'content_type': 'article', 'content': 'Important theorems about limits.', 'order': 3, 'duration': timedelta(minutes=8), 'is_published': True},
                    ],
                    [
                        {'name': 'Basic Differentiation', 'content_type': 'article', 'content': 'Learning basic differentiation techniques.', 'order': 1, 'duration': timedelta(minutes=14), 'is_published': True},
                        {'name': 'Advanced Differentiation', 'content_type': 'video', 'content': 'Advanced differentiation methods.', 'order': 2, 'duration': timedelta(minutes=18), 'is_published': True},
                        {'name': 'Applications of Differentiation', 'content_type': 'article', 'content': 'Applying differentiation in real-world problems.', 'order': 3, 'duration': timedelta(minutes=20), 'is_published': True},
                    ],
                    [
                        {'name': 'Introduction to Integrals', 'content_type': 'video', 'content': 'Overview of integral calculus.', 'order': 1, 'duration': timedelta(minutes=16), 'is_published': True},
                        {'name': 'Techniques of Integration', 'content_type': 'article', 'content': 'Different techniques for solving integrals.', 'order': 2, 'duration': timedelta(minutes=15), 'is_published': True},
                        {'name': 'Applications of Integrals', 'content_type': 'article', 'content': 'Real-world applications of integrals.', 'order': 3, 'duration': timedelta(minutes=22), 'is_published': True},
                    ]
                ]

            # Create modules and lessons
            for i, module_info in enumerate(module_data):
                module = Module.objects.create(
                    course=course,
                    name=module_info['name'],
                    description=module_info['description'],
                    order=module_info['order']
                )
                self.stdout.write(self.style.SUCCESS(f"Created Module: {module.name} for Course: {course.name}"))

                # Create lessons for each module
                for lesson_info in lesson_data[i]:
                    lesson = Lesson.objects.create(
                        module=module,
                        name=lesson_info['name'],
                        content_type=lesson_info['content_type'],
                        content=lesson_info['content'],
                        order=lesson_info['order'],
                        duration=lesson_info['duration'],
                        is_published=lesson_info['is_published']
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created Lesson: {lesson.name} in Module: {module.name}"))
