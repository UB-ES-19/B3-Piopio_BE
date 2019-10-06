from rest_framework import generics, status, views, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from piopio_be import serializers, models, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.


class UserView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserDefaultSerializer
    permission_classes = (permissions.PermissionMapper,)
    has_permissions = {
        permissions.AnonPermissionOnly: ['create'],
        AllowAny: ['retrieve', 'list'],
    }
    has_object_permissions = {
        permissions.IsUserOwner: ['update', 'partial_update', 'destroy'],
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        return serializers.UserDefaultSerializer

    def retrieve(self, request, *args, **kwargs):
        print(kwargs['pk'])
        if kwargs['pk'].isdigit():
            return super(UserView, self).retrieve(request, *args, **kwargs)
        else:
            q = self.queryset.filter(username=kwargs['pk']).first()
            s = self.get_serializer(q)
            return Response(s.data)

    @action(methods=['GET'], detail=False, permission_classes=(IsAuthenticated,), url_path="me", url_name="user_me")
    def me(self, request):
        q = self.queryset.filter(pk=request.user.pk).first()
        s = self.get_serializer(q)
        return Response(s.data)

