from django.shortcuts import render
from rest_framework import generics, status, views, viewsets
from piopio_be import serializers, models
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase


# Create your views here.
class UserView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserCreateSerializer


class MyTokenObtainPairView(TokenViewBase):
    serializer_class = serializers.TokenObtainPairSerializer
