# API serializers
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers, exceptions
from piopio_be.models import User, Profile, Post, Media, Notification, TrendingTopic
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions


class UserProfileSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'banner_url',
            'avatar_url',
            'birthday',
            'description'
        ]


class UserUpdateSerializer(WritableNestedModelSerializer):

    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile",
            "following_count",
            "follower_count",
        ]
        read_only_fields = ('id', 'username', 'email', "following_count", "follower_count", )

class UserDefaultSerializer(WritableNestedModelSerializer):

    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile",
            "following_count",
            "follower_count",
            "followers",
            "followings",
            "blocked_users"
        ]

class UserBlockedSerializers(WritableNestedModelSerializer):

    profile = UserProfileSerializer(required=True)
    user_blocked = serializers.BooleanField()
    other_blocked = serializers.BooleanField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile",
            "following_count",
            "follower_count",
            "followers",
            "followings",
            "blocked_users",
            "user_blocked",
            "other_blocked"
        ]

class UserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile",
            "password",
            "confirm_password",
        ]

    def validate_password(self, value):
        try:
            validate_password(value)
        except exceptions.ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.pop('confirm_password')
        if password != password2:
            raise serializers.ValidationError("passwords must match")
        return attrs

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class MediaSerializer(WritableNestedModelSerializer):

    url = serializers.CharField(required=True)

    class Meta:
        fields = ('url',)
        model = Media


class PostSerializer(WritableNestedModelSerializer):

    media = MediaSerializer(required=False, source="media_set", many=True)

    class Meta:
        fields = ('id', 'content', 'type', 'media', )
        write_only = ('content', 'type', 'media',)
        model = Post


#Serializers to show nested manytomany relations
class EachUserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'username')
        model = User


class PostSerializerWithUser(serializers.ModelSerializer):
    user = UserDefaultSerializer(read_only=True)
    media = MediaSerializer(read_only=True, source="media_set", many=True)
    mentions = EachUserSerializer(many=True, read_only=True)

    class Meta:
        fields = ('id', 'content', 'type', 'media', 'user', 'created_at', 'favorited_count', 'retweeted_count', 'mentions')
        model = Post

class PostSerializerWithParent(serializers.ModelSerializer):
    user = UserDefaultSerializer(read_only=True)
    media = MediaSerializer(read_only=True, source="media_set", many=True)
    mentions = EachUserSerializer(many=True, read_only=True)

    class Meta:
        fields = ('id', 'content', 'type', 'media', 'user', 'created_at', 'favorited_count', 'retweeted_count', 'mentions','parent')
        model = Post

class PostSerializerWithParentLikesRt(serializers.ModelSerializer):
    user = UserDefaultSerializer(read_only=True)
    media = MediaSerializer(read_only=True, source="media_set", many=True)
    mentions = EachUserSerializer(many=True, read_only=True)

    class Meta:
        fields = ('id', 'content', 'type', 'media', 'user', 'created_at', 'favorited_count', 'retweeted_count', 'mentions','parent', 'liked', 'retweeted')
        model = Post

class PostSerializerWithParentLikesRtReport(serializers.ModelSerializer):
    user = UserDefaultSerializer(read_only=True)
    media = MediaSerializer(read_only=True, source="media_set", many=True)
    mentions = EachUserSerializer(many=True, read_only=True)
    blocked = serializers.BooleanField()

    class Meta:
        fields = ('id', 'content', 'type', 'media', 'user', 'created_at', 'favorited_count', 'retweeted_count', 'mentions','parent', 'liked', 'retweeted', 'blocked')
        model = Post

class PostSerializerWLikedRetweet(serializers.ModelSerializer):
    liked = serializers.CharField()
    retweeted = serializers.CharField()
    user = UserDefaultSerializer(read_only=True)
    media = MediaSerializer(read_only=True, source="media_set", many=True)

    class Meta:
        fields = ('id', 'content', 'type', 'media', 'user', 'created_at', 'liked', 'retweeted', 'favorited_count', 'retweeted_count')
        model = Post

class PostSerializerWLikedRetweetMentions(serializers.ModelSerializer):
    liked = serializers.CharField()
    retweeted = serializers.CharField()
    user = UserDefaultSerializer(read_only=True)
    media = MediaSerializer(read_only=True, source="media_set", many=True)
    mentions = EachUserSerializer(many=True, read_only=True)

    class Meta:
        fields = ('id', 'content', 'type', 'media', 'user', 'created_at', 'liked', 'retweeted', 'favorited_count', 'retweeted_count', 'mentions')
        model = Post

class PostSerializerWLikedRetweetMentionsReport(serializers.ModelSerializer):
    liked = serializers.CharField()
    retweeted = serializers.CharField()
    user = UserDefaultSerializer(read_only=True)
    media = MediaSerializer(read_only=True, source="media_set", many=True)
    mentions = EachUserSerializer(many=True, read_only=True)
    blocked = serializers.BooleanField()

    class Meta:
        fields = ('id', 'content', 'type', 'media', 'user', 'created_at', 'liked', 'retweeted', 'favorited_count', 'retweeted_count', 'mentions', 'blocked')
        model = Post

class FollowerSerializer(serializers.ModelSerializer):
    followers = EachUserSerializer(many=True, read_only= True)
    #followings = EachUserSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('followers','id','username')

class FollowingSerializer(serializers.ModelSerializer):
    followings = EachUserSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('followings', 'id', 'username')



class FollowerDetailSerializer(serializers.ModelSerializer):
    followers = EachUserSerializer(many=True, read_only= True)
    #followings = EachUserSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('followers','id','username')

class FollowingDetailSerializer(serializers.ModelSerializer):
    #followers = EachUserSerializer(many=True, read_only= True)
    followings = EachUserSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('followings','id','username')


class NotificationsSerializer(serializers.ModelSerializer):
    user_mentioning = UserDefaultSerializer(read_only=True)
    user_mentioned = UserDefaultSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('user_mentioning', 'user_mentioned', 'post', 'notified')


class TrendingTopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrendingTopic
        fields = ('hashtag', 'count',)