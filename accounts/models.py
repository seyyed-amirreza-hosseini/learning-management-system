from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'ST', _('Student')
        TEACHER = 'TE', _('Teacher')
        ADMIN = 'AD', _('Admin')
    role = models.CharField(max_length=2, choices=Role, default=Role.STUDENT)

    