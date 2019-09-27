from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(default="Jhon ",max_length=30)
    last_name = models.CharField(default="Ash ",max_length=150)


class User(models.Model):
    username = models.CharField(default="Jhon ",max_length=30)
    email = models.EmailField(default="user@gmail.com") 
    password = models.CharField(max_length=50)
    
    def __str__(self):
        return self.username