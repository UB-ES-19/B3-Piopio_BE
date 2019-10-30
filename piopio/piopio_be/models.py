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

    REQUIRED_FIELDS = ['email', 'password']
    USERNAME_FIELD = 'username'

    def follow_user(self, username):
        other = UserProfile.objects.get(user__username=username)
        if not self.is_following(username):
            self.followings.add(other)
            self.following_count = self.followings.all().count()
            self.save()
            other.followers.add(self)
            other.follower_count = other.followers.all().count()
            other.save()
            return True
        else:
            return False


    def unfollow_user(self, username):
            other = UserProfile.objects.get(user__username=username)
            if self.is_following(username):
                self.followings.remove(other)
                self.following_count = self.followings.all().count()
                self.save()
                other.followers.remove(self)
                other.follower_count = other.followers.all().count()
                other.save()
                return True
            else:
                return False

    def is_following(self, username):  #returns Bool
        return self.followings.all().filter(username=username).exists()

    def is_followed_by(self, username):  #returns Bool
        return self.followers.all().filter(username=username).exists()


    objects = PiopioUserManager()

    def __str__(self):
        return self.username


class Profile(models.Model):
    first_name = models.CharField(default="Jhon ", max_length=30)
    last_name = models.CharField(default="Ash ", max_length=150)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

    class Meta:
        ordering = ('created_at',)

