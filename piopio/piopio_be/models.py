from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from piopio_be.managers import PiopioUserManager
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import re


USERNAME_REGEX = '^[a-zA-Z0-9-_]*$'
MENTION_REGEX1 = r'\s[@][a-zA-Z0-9-_]+[\s\W]' # Match space+@user+[space or non-word char]
MENTION_REGEX2 = r'^[@][a-zA-Z0-9-_]+[\s\W]' # 4 regex because I do not why (^|\s) and (\s|$) do not work
MENTION_REGEX3 = r'[@][a-zA-Z0-9-_]+$' #
MENTION_REGEX4 = r'^[@][a-zA-Z0-9-_]+$'

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
    reported =  models.ManyToManyField('Post',related_name="reported",symmetrical = False)

    # Followings and followers
    followings = models.ManyToManyField('self', related_name='following', symmetrical=False)
    followers = models.ManyToManyField('self', related_name='follower', symmetrical=False)
    following_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)

    # Blocked users
    blocked_users = models.ManyToManyField('self', related_name='blocked')

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


class PostManager(models.Manager):
    """
    Custom manager for posts to allow filter blocked users.
    """
    def get_queryset(self):
        return ManagerQuerySet(self.model, using=self._db)

class ManagerQuerySet(models.QuerySet):
    """
    Custom QuerySet for posts to allow filter blocked users.
    """

    def filter_blocked(self, user):
        blocked_users_id = User.blocked_users.through.objects.filter(from_user=user).values_list('to_user_id',flat=True)
        blocked_users_id2 = User.blocked_users.through.objects.filter(to_user=user).values_list('from_user_id',flat=True)

        return self.exclude(user_id__in=blocked_users_id).exclude(user_id__in=blocked_users_id2)


class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    user = models.ForeignKey(User, related_name="post_author", on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    parent = models.ManyToManyField('self',related_name="child",symmetrical = False)
    # Likes and retweets
    likes = models.ManyToManyField(User, related_name="post_likes", through='LikedTable')
    retweets = models.ManyToManyField(User, related_name="post_retweets", through='RetweetedTable')
    favorited_count = models.IntegerField(default=0)
    retweeted_count = models.IntegerField(default=0)

    objects = PostManager()

    def __str__(self):
        return self.content

    class Meta:
        ordering = ('created_at',)

    @property
    def mentions(self):
        users_ids = Notification.objects.filter(post=self).values_list('user_mentioned', flat=True)
        return User.objects.filter(id__in=users_ids)

    def serializeCustom(self):
        data = { 
            "author": self.user,
            "created_at": self.created_at,
            "content": self.content,
            "favorited_count": self.favorited_count,
            "retweeted_count": self.retweeted_count,
            "parent": self.parent,
        }
        return data


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


class Notification(models.Model):
    user_mentioning = models.ForeignKey(User, related_name="user_mentioning", on_delete=models.CASCADE)
    user_mentioned = models.ForeignKey(User, related_name="user_mentioned", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    notified = models.BooleanField(default=False)


class TrendingTopic(models.Model):
    hashtag = models.CharField(max_length=200)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(db_index=True, auto_now_add=False)


@receiver(post_save, sender=Post)
def post_post_save(sender, instance, **kwargs):
    """
    When a post is saved, if it contains a reference create a new notification.
    """
    content = instance.content
    matches = re.findall(MENTION_REGEX1, content)
    matches += re.findall(MENTION_REGEX2, content)
    matches += re.findall(MENTION_REGEX3, content)
    matches += re.findall(MENTION_REGEX4, content)

    HASHTAG_REGEX = r'#(\w+)\b'
    hashtag_matches = re.findall(HASHTAG_REGEX, content)

    for hashtag in hashtag_matches:
        try:
            ref = TrendingTopic.objects.get(hashtag=hashtag)
            ref.count += 1
            ref.save()
        except ObjectDoesNotExist:
            TrendingTopic.objects.create(hashtag=hashtag, count=1, created_at=timezone.now())

    users_notified = []
    blocked_users = instance.user.blocked_users.all().values_list('id', flat=True)

    for match in matches:
        user = re.findall(r'[a-zA-Z0-9-_]+', match)

        if len(user) != 0:
            # The username will always be the first match
            user = user[0]

            user_search = User.objects.filter(username=user)
            if user_search.exists():
                user_search = user_search.first()
                if user_search.id not in users_notified and user_search.id not in blocked_users:
                    Notification.objects.create(user_mentioning=instance.user, user_mentioned=user_search, post=instance)
                    users_notified.append(user_search.id)


@receiver(post_save, sender=LikedTable)
def like_post_save(sender, instance, **kwargs):
    """
    When a post is liked add it to the counter
    """
    try:
        # Update the number of likes
        num_reviews = Post.objects.get(id=instance.post_id)
        num_reviews.favorited_count += 1
        num_reviews.save()
    except Post.DoesNotExist:
        # Never should happen
        return


@receiver(post_delete, sender=LikedTable)
def like_post_delete(sender, instance, **kwargs):
    """
    When a post has the liked removed substract it from to the counter
    """
    try:
        # Update the number of likes
        num_reviews = Post.objects.get(id=instance.post_id)
        num_reviews.favorited_count -= 1
        num_reviews.save()
    except Post.DoesNotExist:
        # Never should happen
        return


@receiver(post_save, sender=RetweetedTable)
def retweet_post_save(sender, instance, **kwargs):
    """
    When a post is retweeted add it to the counter
    """
    try:
        # Update the number of retweets
        num_reviews = Post.objects.get(id=instance.post_id)
        num_reviews.retweeted_count += 1
        num_reviews.save()
    except Post.DoesNotExist:
        # Never should happen
        return


@receiver(post_delete, sender=RetweetedTable)
def retweet_post_delete(sender, instance, **kwargs):
    """
    When a post has the retweet removed substract it from to the counter
    """
    try:
        # Update the number of retweets
        num_reviews = Post.objects.get(id=instance.post_id)
        num_reviews.retweeted_count -= 1
        num_reviews.save()
    except Post.DoesNotExist:
        # Never should happen
        return
