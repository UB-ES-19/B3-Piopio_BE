from rest_framework import generics, status, views, viewsets
from piopio_be import serializers, models
from rest_framework.response import Response
import rest_framework_simplejwt


# Create your views here.
class UserView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserCreateSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Add permissions to each action
        # if self.action == 'retrieve' or self.action == 'list':
        #     permission_classes = [permissions.IsAuthenticated]
        # else:
        permission_classes = []
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """
        User can only be destroyed by an admin or by themselves
        """
        instance = self.get_object()
        if instance.email == request.user.email or request.user.is_superuser:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise rest_framework_simplejwt.exceptions.AuthenticationFailed(
                self.error_messages['required_credentials']
            )
