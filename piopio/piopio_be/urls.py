from rest_framework.routers import DefaultRouter
from piopio_be import views

router = DefaultRouter()
router.register("users", views.UserView)

urlpatterns = router.urls
