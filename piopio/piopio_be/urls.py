from rest_framework.routers import DefaultRouter
from piopio_be import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.urls import path, re_path
from rest_framework_nested import routers
from django.conf.urls import include, url

router = DefaultRouter()
router.register(r'users', views.UserView, basename='users')
router.register(r'posts', views.PostView, basename='posts')
router.register(r'follows', views.UserFollowerView, basename='follower')
router.register(r'followings', views.UserFollwoingView, basename='following')

users_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
users_router.register(r'posts', views.PostsFromUserView)
users_router.register(r'follows', views.UserNestedFollowerView)
users_router.register(r'followings', views.UserNestedFollowingsView)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(users_router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify')
]
