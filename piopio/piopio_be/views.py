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


class PostsFromUserView(viewsets.ReadOnlyModelViewSet):
    """
    Nested view for retrieving and listing the posts of a user
    """
    queryset = models.Post.objects.all().order_by('created_at')
    permission_classes = (IsAuthenticated,)

    def list(self, request, user_pk=None, *args, **kwargs):
        posts = self.get_queryset().filter(user_id=user_pk).values()
        serialized_posts = serializers.PostSerializer(posts, many=True)
        return Response(serialized_posts.data)

    def retrieve(self, request, pk=None, user_pk=None, *args, **kwargs):
        posts = self.get_queryset().get(pk=pk)
        serialized_posts = serializers.PostSerializer(posts)
        return Response(serialized_posts.data)


class PostView(viewsets.ModelViewSet):
    queryset = models.Post.objects.all().order_by('created_at')
    serializer_class = serializers.PostSerializerWithUser
    permission_classes = (permissions.PermissionMapper,)
    has_permissions = {
        IsAuthenticated: ['create'],
    }

    has_object_permissions = {
        permissions.IsUserOwnerOrAdmin: ['update', 'partial_update', 'destroy'],
    }

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=request.user.pk)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
            serializer = self.serializer_class(post)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = self.serializer_class(post, data=request.data)
            if serializer.is_valid():
                serializer.save(user_id=request.user.pk)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False, permission_classes=(IsAuthenticated,), url_path="me",
            url_name="posts_me")
    def me(self, request):
        """
        Returns the list of the authenticated user's posts.
        """
        user = request.user
        posts = self.get_queryset().filter(user_id=user.pk).values()
        serialized_posts = serializers.PostSerializer(posts, many=True)
        return Response(serialized_posts.data)
