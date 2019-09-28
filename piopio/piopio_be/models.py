from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from piopio_be.managers import PiopioUserManager


class Profile(models.Model):
    first_name = models.CharField(default="Jhon ", max_length=30)
    last_name = models.CharField(default="Ash ", max_length=150)

    def __str__(self):
        return str(self.first_name)+" "+str(self.last_name)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    REQUIRED_FIELDS = ['email', 'password']
    USERNAME_FIELD = 'username'

    objects = PiopioUserManager()

    def __str__(self):
        return self.username