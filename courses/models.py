from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'BE', _('Beginner')
        INTERMEDIATE = 'IN', _('Intermediate')
        ADVANCED = 'AD', _('Advanced')

    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField()
    level = models.CharField(max_length=2, choices=Level, default=Level.BEGINNER)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    instructors = models.ManyToManyField(settings.AUTH_USER_MODEL, through='InstructorCourse')


# Intermediate Table
class InstructorCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_date = models.DateField()
    role = models.CharField(max_length=100)
