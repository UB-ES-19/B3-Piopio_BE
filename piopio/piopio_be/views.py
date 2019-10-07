from rest_framework import generics, status, views, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view

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
        if kwargs['pk'].isdigit():
            return super(UserView, self).retrieve(request, *args, **kwargs)
        else:
            print(kwargs['pk'])
            q = self.queryset.filter(username=kwargs['pk']).first()
            if q is None:
                return Response({'detail': 'User Not Found'}, status.HTTP_404_NOT_FOUND)
            s = self.get_serializer(q)
            return Response(s.data)

    @action(methods=['GET'], detail=False, permission_classes=(IsAuthenticated,), url_path="me", url_name="user_me")
    def me(self, request):
        q = self.queryset.filter(pk=request.user.pk).first()
        s = self.get_serializer(q)
        return Response(s.data)


class PostView(viewsets.ModelViewSet):
    posts = models.Post.objects.all()
    serializer_class = serializers.PostSerializer

    @api_view(['GET', 'POST'])
    def post_list(self, request):
        """
            Retrieve all post.
        """
        if request.method == 'GET':
            posts = models.Post.objects.all()
            serializer = serializers.PostSerializer(posts, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = serializers.PostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', 'PUT', 'DELETE'])
    def post_detail(self, request, pk):
        """
        Retrieve, update or delete a post.
        """
        try:
            post = models.Post.objects.get(pk=pk)
        except post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = serializers.PostSerializer(post)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = serializers.PostSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

