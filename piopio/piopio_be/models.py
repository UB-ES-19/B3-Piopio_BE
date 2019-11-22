from django.utils import timezone
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from piopio_be.managers import PiopioUserManager


USERNAME_REGEX = '^[a-zA-Z0-9-_]*$'


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message='Username must be alphanumeric or contain any of the following: "_ -" ',
                code='invalid_username'
            )],
        unique=True,
    )
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='date joined')
    followings = models.ManyToManyField('self', related_name='following', symmetrical=False)
    followers = models.ManyToManyField('self', related_name='follower', symmetrical=False)
    following_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)
    favorited = models.ManyToManyField("Post",related_name="favorited",symmetrical=False)
    retweeted = models.ManyToManyField("Post",related_name="retweeted",symmetrical=False)

    REQUIRED_FIELDS = ['email', 'password']
    USERNAME_FIELD = 'username'


    objects = PiopioUserManager()

    def __str__(self):
        return self.username


class Profile(models.Model):
    first_name = models.CharField(default="Jhon ", max_length=30)
    last_name = models.CharField(default="Ash ", max_length=150)
    banner_url = models.CharField(max_length=100, blank=True)
    avatar_url = models.CharField(max_length=100, blank=True)
    birthday = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=240, blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    favorited_count = models.IntegerField(default=0)
    retweeted_count = models.IntegerField(default=0)

    def __str__(self):
        return self.content

    class Meta:
        ordering = ('created_at',)


class Media(models.Model):
    url = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.url

    class Meta:
        ordering = ('created_at',)