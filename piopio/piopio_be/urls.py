from rest_framework.routers import DefaultRouter
from piopio_be import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.urls import path, re_path

router = DefaultRouter()
router.register("users", views.UserView)
router.register("posts", views.PostView)

urlpatterns = router.urls

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify')
]
