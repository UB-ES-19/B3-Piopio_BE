from rest_framework import generics, status, views, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view

from piopio_be import serializers, models, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_list_or_404, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Subquery, Value, DateTimeField, F, CharField, OuterRef
from piopio_be.django_custom_join import join_to_queryset
# Create your views here.
from django.db.models import Case, When, Q


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
        if self.action == 'update':
            return serializers.UserUpdateSerializer
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

    @action(methods=['POST'], detail=False, url_path="like/(?P<postpk>[^/.]+)", permission_classes=(IsAuthenticated,), url_name="user_like")
    def like(self, request, postpk):
        return self.add_field_tweet(postpk, request, models.LikedTable, "Liked", "Removed like")

    @action(methods=['POST'], detail=False, url_path="retweet/(?P<postpk>[^/.]+)",
            permission_classes=(IsAuthenticated,), url_name="user_retweet")
    def tweet(self, request, postpk):
        return self.add_field_tweet(postpk, request, models.RetweetedTable, "Retweeted", "Removed retweet")

    def add_field_tweet(self, postpk, request, model, pos_msg, neg_msg):
        user = self.queryset.get(pk=request.user.pk)
        post = get_object_or_404(models.Post, pk=postpk)
        post_to_remove = model.objects.filter(user=user).filter(post=post)
        if post_to_remove.count() != 0:
            # Delete like
            post_to_remove.first().delete()
            return Response({'message': neg_msg}, status.HTTP_200_OK)
        else:
            # Create like
            model.objects.create(user=user, post=post)
            return Response({'message': pos_msg}, status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=False, url_path="(?P<userpk>[^/.]+)/liked", url_name="user_liked")
    def liked(self, request, userpk):
        user = get_object_or_404(models.User, pk=userpk)

        filtered_posts = models.LikedTable.objects.filter(user=user)
        posts_liked = filtered_posts.values_list('post', flat=True)
        sorted_posts = filtered_posts.order_by('post_id')
        posts = models.Post.objects.filter(id__in=posts_liked)
        # TODO: sort by liked date

        posts = add_likes_and_retweets(posts, user)
        page = self.paginate_queryset(posts)
        serialized_posts = serializers.PostSerializerWLikedRetweet(
            page, many=True)
        return self.get_paginated_response(serialized_posts.data)

    @action(methods=['GET'], detail=False, url_path="(?P<userpk>[^/.]+)/retweeted", url_name="user_retweeted")
    def retweeted(self, request, userpk):
        user = get_object_or_404(models.User, pk=userpk)

        filtered_posts = models.RetweetedTable.objects.filter(user=user)
        posts_retweeted = filtered_posts.values_list('post', flat=True)
        sorted_posts = filtered_posts.order_by('post_id')
        posts = models.Post.objects.filter(id__in=posts_retweeted)
        # TODO: sort by retweeted date

        posts = add_likes_and_retweets(posts, user)
        page = self.paginate_queryset(posts)
        serialized_posts = serializers.PostSerializerWLikedRetweet(
            page, many=True)
        return self.get_paginated_response(serialized_posts.data)

    @action(methods=['GET'], detail=False, permission_classes=(IsAuthenticated,),
            url_path="(?P<userpk>[^/.]+)/all_related", url_name="all_related_post")
    def related(self, request, userpk):
        """
        Returns the list of followers & user's posts.
        """
        related = []
        followings = models.User.objects.all().get(id=userpk).followings.values()
        for _user in followings:
            print(_user)
            related.append(_user['id'])

        related.append(userpk)
        posts = models.Post.objects.filter(
            user_id__in=related).order_by('-created_at')
        posts = add_likes_and_retweets(posts, userpk)

        """
        Filter the results with user's report list
        """
        user = self.queryset.get(pk=request.user.pk)
        reported = user.reported.all().values_list('id')
        filtered = posts.all().exclude(id__in=reported)

        page = self.paginate_queryset(filtered)
        serialized_posts = serializers.PostSerializerWLikedRetweet(
            page, many=True)
        return self.get_paginated_response(serialized_posts.data)

    @action(methods=['GET'], detail=False, url_path="notifications", permission_classes=(IsAuthenticated,), url_name="user_notifications")
    def notifications(self, request):
        user_notifications = models.Notification.objects.filter(
            user_mentioned=request.user)
        page = self.paginate_queryset(user_notifications)
        serialized_users = serializers.NotificationsSerializer(page, many=True)
        return self.get_paginated_response(serialized_users.data)

    @action(methods=['POST'], detail=False, url_path="report/(?P<postpk>[^/.]+)", permission_classes=(IsAuthenticated,), url_name="user_report")
    def report(self, request, postpk):
        try:
            user = self.queryset.get(pk=request.user.pk)
            post = get_object_or_404(models.Post, pk=postpk)
            user.reported.add(post.id)
            return Response({'message':'reported!'}, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({'message': 'Something went wrong!'}, status.HTTP_404_NOT_FOUND)
        except models.User.DoesNotExist:
            return Response({'message': 'Something went wrong!'}, status.HTTP_404_NOT_FOUND)
        


def add_likes_and_retweets(posts, user, sort=True):
    # Add liked field
    liked_posts = models.LikedTable.objects.filter(
        user=user).values_list('post', flat=True)
    posts = posts.annotate(liked=Case(When(id__in=liked_posts, then=Value(
        'true')), default=Value('false'), output_field=CharField()))

    # Add retweeted field
    retweeted_posts = models.RetweetedTable.objects.filter(
        user=user).values_list('post', flat=True)
    posts = posts.annotate(retweeted=Case(When(id__in=retweeted_posts, then=Value(
        'true')), default=Value('false'), output_field=CharField()))

    if sort:
        posts = posts.order_by('-created_at')

    return posts


def sort_posts_and_retweets(posts, retweets, ids, user):
    posts = posts | retweets
    posts = posts.annotate(sort_date=Case(When(id__in=ids,
                                               then=Subquery(models.RetweetedTable.objects.filter(post=OuterRef('id')).filter(user=user)[:1].values_list('retweeted_date', flat=True))),
                                          default=F('created_at'), output_field=DateTimeField()))

    posts = posts.order_by('-sort_date')
    return posts


class PostsFromUserView(viewsets.ReadOnlyModelViewSet):
    """
    Nested view for retrieving and listing the posts of a user
    """
    queryset = models.Post.objects.all().order_by('created_at')
    permission_classes = (IsAuthenticated,)

    def list(self, request, user_pk=None, *args, **kwargs):
        posts = self.get_queryset().filter(user_id=user_pk)
        retweets = models.RetweetedTable.objects.filter(user=user_pk)
        ids = retweets.values_list('post', flat=True)

        posts = sort_posts_and_retweets(
            posts, self.get_queryset().filter(id__in=ids), ids, user_pk)

        posts = add_likes_and_retweets(posts, request.user, sort=False)

        page = self.paginate_queryset(posts)
        serialized_posts = serializers.PostSerializerWLikedRetweet(
            page, many=True)
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

    def get_serializer_with_parent(self):
        return serializers.PostSerializerWithParent

    def get_serializer_parent(self, *args, **kwargs):
        serializer_class = self.get_serializer_with_parent()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=request.user.pk)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
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
        Returns the list of the authenticated user's posts and their retweets
        """
        user = request.user
        posts = self.get_queryset().filter(user_id=user.pk)
        ids = models.RetweetedTable.objects.filter(
            user=user).values_list('post', flat=True)
        posts = posts | self.get_queryset().filter(id__in=ids)
        posts = add_likes_and_retweets(posts, user)
        page = self.paginate_queryset(posts)
        serialized_posts = serializers.PostSerializerWLikedRetweet(
            page, many=True)
        return self.get_paginated_response(serialized_posts.data)

    @action(methods=['GET'], detail=False, url_path="search", url_name="posts_search")
    def search(self, request):
        try:
            content = request.query_params.get('content')
            contents = content.split(" ")
            posts_queryset = self.queryset

            """
            Filter the results with user's report list
            """
            user = self.queryset.get(pk=request.user.pk)
            reported = user.reported.all().values_list('id')

            for content in contents:
                posts_queryset = posts_queryset.filter(
                    content__icontains=content).exclude(id__in=reported) #Search result excluded reported post

        except ValueError:
            return Response({'content': 'Not specified'}, status.HTTP_404_NOT_FOUND)

        posts_queryset = add_likes_and_retweets(posts_queryset, request.user)
        page = self.paginate_queryset(posts_queryset)
        serialized_posts = serializers.PostSerializerWLikedRetweet(
            page, many=True)
        return self.get_paginated_response(serialized_posts.data)

    @action(methods=['GET'], detail=False, url_path="details/(?P<postpk>[^/.]+)", url_name="detail_post")
    def details(self, request, postpk):
        try:
            post = self.get_queryset().filter(id=postpk)
            parent = post.get().parent.all()
            child = self.get_queryset().filter(parent__id__exact=postpk)
            parent_rslt = self.get_serializer(parent.get()).data
            post_rslt = self.get_serializer(post.get()).data
            child_rslt = [self.get_serializer(_child).data for _child in child]
            data = {
                "Details": {
                    "parent": parent_rslt,
                    "post": post_rslt,
                    "childs": child_rslt
                }
            }
            return Response(data)

        except ValueError:
            return Response({'message': 'Something went wrong!'}, status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=False, url_path="(?P<postpk>[^/.]+)/reply", permission_classes=(IsAuthenticated,), url_name="reply_post")
    def reply(self, request, postpk):
        try:
            parent = self.get_queryset().filter(id=postpk)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user_id=request.user.pk)
            headers = self.get_success_headers(serializer.data)
            child_id = serializer.data['id']
            tmp = self.get_queryset().filter(id=child_id)
            tmp.get().parent.add(parent.get().id)
            tmp.get().save()
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except ValueError:
            return Response({'message': 'Something went wrong!'}, status.HTTP_404_NOT_FOUND)
        except models.Post.DoesNotExist:
            return Response({'message': 'Something went wrong!'}, status.HTTP_404_NOT_FOUND)


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
        else:  # retrieve
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
        else:  # retrieve
            return serializers.UserDefaultSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        followings = instance.followings.all()
        page = self.paginate_queryset(followings)
        serialized_followings = self.get_serializer(page, many=True)
        return self.get_paginated_response(serialized_followings.data)


class UserNestedFollowerView(viewsets.GenericViewSet,
                             mixins.ListModelMixin):
    """
    Nested view for retrieving and listing the posts of a user
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserDefaultSerializer

    def list(self, request, user_pk=None, *args, **kwargs):
        posts = self.get_queryset().get(pk=user_pk)
        followers = posts.followers.all()
        page = self.paginate_queryset(followers)
        serialized_posts = self.get_serializer(page, many=True)
        return self.get_paginated_response(serialized_posts.data)


class UserNestedFollowingsView(viewsets.ReadOnlyModelViewSet):
    """
    Nested view for retrieving and listing the posts of a user
    """
    queryset = models.User.objects.all()
    serializer_class = serializers.UserDefaultSerializer

    def list(self, request, user_pk=None, *args, **kwargs):
        posts = self.get_queryset().get(pk=user_pk)
        followings = posts.followers.all()
        page = self.paginate_queryset(followings)
        serialized_posts = self.get_serializer(page, many=True)
        return self.get_paginated_response(serialized_posts.data)


class NotificationsView(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationsSerializer

    @action(methods=['POST'], detail=False, permission_classes=(IsAuthenticated,), url_path="notified", url_name="notifications_notified")
    def notified(self, request):
        try:
            post_id = request.data.get('post')
            notification = self.queryset.get(
                user_mentioned=request.user, post__id=post_id)
        except ValueError:
            return Response({'post': 'Not specified'}, status.HTTP_404_NOT_FOUND)
        except models.Notification.DoesNotExist:
            return Response({'notification': 'Unable to update notification'}, status.HTTP_404_NOT_FOUND)

        notification.notified = True
        notification.save()
        serialized_notification = self.get_serializer(notification)

        return Response(serialized_notification.data)
