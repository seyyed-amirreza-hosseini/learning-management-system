from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True)

    class Role(models.TextChoices):
        STUDENT = 'ST', _('Student')
        TEACHER = 'TE', _('Teacher')
        ADMIN = 'AD', _('Admin')
    role = models.CharField(max_length=2, choices=Role, default=Role.STUDENT)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
