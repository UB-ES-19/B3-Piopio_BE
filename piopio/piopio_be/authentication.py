from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailAuthentication(ModelBackend):
    """
    Custom authentication to allow the user to be identified with its email.
    """
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        if username is not None:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except User.DoesNotExist:
                return None

        elif email is not None:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except User.DoesNotExist:
                return None
