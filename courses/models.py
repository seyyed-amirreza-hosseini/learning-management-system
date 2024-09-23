from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxLengthValidator


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'BE', _('Beginner')
        INTERMEDIATE = 'IN', _('Intermediate')
        ADVANCED = 'AD', _('Advanced')

    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField()
    level = models.CharField(max_length=2, choices=Level, default=Level.BEGINNER)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    instructors = models.ManyToManyField(settings.AUTH_USER_MODEL, through='InstructorCourse')


# Intermediate Table
class InstructorCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_date = models.DateField()
    role = models.CharField(max_length=100)


class Module(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Lesson(models.Model):
    class ContentType(models.TextChoices):
        VIDEO = 'video', 'Video'
        ARTICLE = 'article', 'Article/Text'
        QUIZ = 'quiz', 'Quiz'
        ASSIGNMENT = 'assignment', 'Assignment'
        PRESENTATION = 'presentation', 'Presentation'
        IMAGE = 'image', 'Image'
        AUDIO = 'audio', 'Audio'
        LIVE_SESSION = 'live_session', 'Live Session'
        PDF = 'pdf', 'PDF'

    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=ContentType)
    content = models.TextField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    order = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    duration = models.DurationField(null=True, blank=True)
    is_published = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resources = models.FileField(upload_to='lesson_resources', null=True, blank=True)


class Assignment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxLengthValidator(20)])
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assignments')
