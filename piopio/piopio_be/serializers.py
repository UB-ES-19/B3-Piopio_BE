# API serializers
from rest_framework import serializers, exceptions
from piopio_be import messages
from piopio_be.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as djangoexceptions
from django.db import IntegrityError, transaction


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    default_error_messages = {
        "cannot_create_user": messages.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = (
            User.USERNAME_FIELD,
            "email",
            "password"
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except djangoexceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create(**validated_data)
            user.is_active = True
            user.save(update_fields=["is_active"])
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