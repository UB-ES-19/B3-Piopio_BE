from rest_framework import generics, status, views, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view

from piopio_be import serializers, models, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.paginator import Paginator

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

    @action(methods=['GET'], detail=False, url_path="search", url_name="user_search")
    def search(self, request):
        try:
            username = request.query_params.get('username')
            users_queryset = self.queryset.filter(username__icontains=username)
        except ValueError:
            return Response({'username': 'Not specified'}, status.HTTP_404_NOT_FOUND)

        page = self.paginate_queryset(users_queryset)
        serialized_users = serializers.UserDefaultSerializer(page, many=True)
        return self.get_paginated_response(serialized_users.data)

    @action(methods=['POST'], detail=False, url_path="follow", permission_classes=(IsAuthenticated,), url_name="user_follow")
    def follow(self, request):
        try:
            username = request.data.get('username')
            other = self.queryset.get(username=username)
            q = self.queryset.filter(pk=request.user.pk).first()

            if other.pk != q.pk:
                if not q.followings.all().filter(username=username).exists():
                    q.followings.add(other)
                    q.following_count = q.following_count + 1
                    q.save()

                    other.followers.add(q)
                    other.follower_count = other.follower_count + 1
                    other.save()
                return Response({'username': "Correct"}, status.HTTP_201_CREATED)

            return Response({'username': 'You can\'t follow yourself'}, status.HTTP_404_NOT_FOUND)

        except ValueError:
            return Response({'username': 'Not specified'}, status.HTTP_404_NOT_FOUND)
        except models.User.DoesNotExist:
            return Response({'username': 'The specified user does not exist'}, status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=False, url_path="unfollow", permission_classes=(IsAuthenticated,), url_name="user_unfollow")
    def unfollow(self, request):
        try:
            username = request.data.get('username')
            other = self.queryset.get(username=username)
            q = self.queryset.filter(pk=request.user.pk).first()

            if other.pk != q.pk:
                if q.followings.all().filter(username=username).exists():
                    q.followings.remove(other)
                    q.following_count = q.following_count - 1
                    q.save()

                    other.followers.remove(q)
                    other.follower_count = other.follower_count - 1
                    other.save()
                return Response({'username': "Correct"}, status.HTTP_201_CREATED)

            return Response({'username': 'You can\'t follow yourself'}, status.HTTP_404_NOT_FOUND)

        except ValueError:
            return Response({'username': 'Not specified'}, status.HTTP_404_NOT_FOUND)
        except models.User.DoesNotExist:
            return Response({'username': 'The specified user does not exist'}, status.HTTP_404_NOT_FOUND)

class PostsFromUserView(viewsets.ReadOnlyModelViewSet):
    """
    Nested view for retrieving and listing the posts of a user
    """
    queryset = models.Post.objects.all().order_by('created_at')
    permission_classes = (IsAuthenticated,)

    def list(self, request, user_pk=None, *args, **kwargs):
        posts = self.get_queryset().filter(user_id=user_pk)
        page = self.paginate_queryset(posts)
        serialized_posts = serializers.PostSerializerWithUser(page, many=True)
        return self.get_paginated_response(serialized_posts.data)

    def retrieve(self, request, pk=None, user_pk=None, *args, **kwargs):
        posts = self.get_queryset().get(pk=pk)
        serialized_posts = serializers.PostSerializerWithUser(posts)
        return Response(serialized_posts.data)


class PostView(viewsets.ModelViewSet):
    queryset = models.Post.objects.all().order_by('-created_at')
    serializer_class = serializers.PostSerializerWithUser
    permission_classes = (permissions.PermissionMapper,)
    has_permissions = {
        IsAuthenticated: ['create'],
    }

    has_object_permissions = {
        permissions.IsPostOwner: ['update', 'partial_update', 'destroy'],
    }

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return serializers.PostSerializer
        return serializers.PostSerializerWithUser

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=request.user.pk)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=request.user.pk)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    @action(methods=['GET'], detail=False, permission_classes=(IsAuthenticated,), url_path="me", url_name="posts_me")
    def me(self, request):
        """
        Returns the list of the authenticated user's posts.
        """
        user = request.user
        posts = self.get_queryset().filter(user_id=user.pk)
        page = self.paginate_queryset(posts)
        serialized_posts = serializers.PostSerializerWithUser(page, many=True)
        return self.get_paginated_response(serialized_posts.data)


class UserFollowerView(viewsets.GenericViewSet,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin):
    """
       Viewset to return all the nested friendship relations.
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.FollowerSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.FollowerSerializer
        else: # retrieve
            return serializers.UserDefaultSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        followers = instance.followers.all()
        page = self.paginate_queryset(followers)
        serialized_followers = self.get_serializer(page, many=True)
        return self.get_paginated_response(serialized_followers.data)


class UserFollwoingView(viewsets.GenericViewSet,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin):
    """
       Viewset to return all the nested friendship relations.
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.FollowingSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.FollowingSerializer
        else: # retrieve
            return serializers.UserDefaultSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        followings = instance.followings.all()
        page = self.paginate_queryset(followings)
        serialized_followings = self.get_serializer(page, many=True)
        return self.get_paginated_response(serialized_followings.data)