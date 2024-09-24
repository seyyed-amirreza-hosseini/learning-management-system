from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True)

    class Role(models.TextChoices):
        STUDENT = 'ST', _('Student')
        TEACHER = 'TE', _('Teacher')
        ADMIN = 'AD', _('Admin')
    role = models.CharField(max_length=2, choices=Role, default=Role.STUDENT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
  