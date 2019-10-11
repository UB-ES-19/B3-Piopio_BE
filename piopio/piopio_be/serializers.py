# API serializers
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers, exceptions
from piopio_be.models import User, Profile,Post
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions


class UserProfileSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name'
        ]


class UserDefaultSerializer(WritableNestedModelSerializer):

    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile",
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


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'content', 'created_at')
        model = Post

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        return Post.objects.create(user_id=user_id, **validated_data)

    def update(self, instance, validated_data):
        instance.content = validated_data.get("content")
        instance.save()
        return instance


class PostSerializerWithUser(PostSerializer):
    user = UserDefaultSerializer(read_only=True)

    class Meta:
        fields = ('id', 'content', 'created_at', 'user')
        model = Post