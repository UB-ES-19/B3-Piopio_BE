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

    # Followings and followers
    followings = models.ManyToManyField('self', related_name='following', symmetrical=False)
    followers = models.ManyToManyField('self', related_name='follower', symmetrical=False)
    following_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)

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
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    user = models.ForeignKey(User, related_name="post_author", on_delete=models.CASCADE)
    type = models.CharField(max_length=10)

    # Likes and retweets
    likes = models.ManyToManyField(User, related_name="post_likes", through='LikedTable')
    retweets = models.ManyToManyField(User, related_name="post_retweets", through='RetweetedTable')
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


class LikedTable(models.Model):
    user = models.ForeignKey(User, related_name="user_liked", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="post_liked", on_delete=models.CASCADE)
    liked_date = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        ordering = ('liked_date',)


class RetweetedTable(models.Model):
    user = models.ForeignKey(User, related_name="user_retweeted", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="post_retweeted", on_delete=models.CASCADE)
    retweeted_date = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        ordering = ('retweeted_date',)


from piopio_be import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=models.LikedTable)
def like_post_save(sender, instance, **kwargs):
    """
    When a post is liked add it to the counter
    """
    try:
        # Update the number of likes
        num_reviews = models.Post.objects.get(id=instance.post_id)
        num_reviews.favorited_count += 1
        num_reviews.save()
    except models.Post.DoesNotExist:
        # Never should happen
        return


@receiver(post_delete, sender=models.LikedTable)
def like_post_delete(sender, instance, **kwargs):
    """
    When a post has the liked removed substract it from to the counter
    """
    try:
        # Update the number of likes
        num_reviews = models.Post.objects.get(id=instance.post_id)
        num_reviews.favorited_count -= 1
        num_reviews.save()
    except models.Post.DoesNotExist:
        # Never should happen
        return


@receiver(post_save, sender=models.RetweetedTable)
def retweet_post_save(sender, instance, **kwargs):
    """
    When a post is retweeted add it to the counter
    """
    try:
        # Update the number of retweets
        num_reviews = models.Post.objects.get(id=instance.post_id)
        num_reviews.retweeted_count += 1
        num_reviews.save()
    except models.Post.DoesNotExist:
        # Never should happen
        return


@receiver(post_delete, sender=models.RetweetedTable)
def retweet_post_delete(sender, instance, **kwargs):
    """
    When a post has the retweet removed substract it from to the counter
    """
    try:
        # Update the number of retweets
        num_reviews = models.Post.objects.get(id=instance.post_id)
        num_reviews.retweeted_count -= 1
        num_reviews.save()
    except models.Post.DoesNotExist:
        # Never should happen
        return
