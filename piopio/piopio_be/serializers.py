# API serializers
from rest_framework import serializers, exceptions
from piopio_be.models import User, Profile
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


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = (
            User.USERNAME_FIELD,
            "email",
            'password'
        )