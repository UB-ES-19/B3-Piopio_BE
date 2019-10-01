from django.utils import timezone
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from piopio_be.managers import PiopioUserManager


USERNAME_REGEX = '^[a-zA-Z0-9.-_]*$'


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message='Username must be alphanumeric or contain any of the following: ". _ -" ',
                code='invalid_username'
            )],
        unique=True,
    )
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='date joined')

    REQUIRED_FIELDS = ['email', 'password']
    USERNAME_FIELD = 'username'

    objects = PiopioUserManager()

    def __str__(self):
        return self.username


class Profile(models.Model):
    first_name = models.CharField(default="Jhon ", max_length=30)
    last_name = models.CharField(default="Ash ", max_length=150)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)