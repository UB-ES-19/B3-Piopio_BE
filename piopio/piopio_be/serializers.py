# API serializers
from rest_framework import serializers, exceptions
from piopio_be import messages
from piopio_be.models import User, Profile
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
import rest_framework_simplejwt
from django.db import IntegrityError, transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import PasswordField

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


## Token serializers

class TokenObtainSerializer(serializers.Serializer):
    username_field = User.USERNAME_FIELD
    email_field = User.email

    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials',
        'required_credentials': 'Username or email is required'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField(required=False)
        self.fields['email'] = serializers.EmailField(required=False)
        self.fields['password'] = PasswordField()

    def validate(self, attrs):
        print(attrs)
        try:
            authenticate_kwargs = {
                self.username_field: attrs[self.username_field],
                'password': attrs['password'],
            }
        except KeyError:
            try:
                authenticate_kwargs = {
                    'email': attrs['email'],
                    'password': attrs['password'],
                }
            except KeyError:
                raise rest_framework_simplejwt.exceptions.AuthenticationFailed(
                    self.error_messages['required_credentials']
                )

        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if self.user is None or not self.user.is_active:
            raise rest_framework_simplejwt.exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        return {}

    @classmethod
    def get_token(cls, user):
        raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializer` subclasses')


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data