from django.shortcuts import render
from rest_framework import generics, status, views, viewsets
from piopio_be import serializers, models
from rest_framework.decorators import action
from rest_framework.response import Response

# Create your views here.
class UserView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_instance(self):
        return self.request.user

    @action(["get", "post"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == "POST":
            return self.create_user(request, *args, **kwargs)
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)

    def create_user(self, request):
        serializer = serializers.UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Check is someone is able to see all the users
        #if not user.is_staff:
        #    queryset = queryset.filter(pk=user.pk)
        return queryset