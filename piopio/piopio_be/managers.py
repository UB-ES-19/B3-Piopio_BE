from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
import piopio_be.models

class PiopioUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create(self, email, username, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email or not password:
            raise ValueError(_('The Email must be set'))

        # Other checks
        email = self.normalize_email(email)

        # Create User profile
        extra_fields["profile"] = piopio_be.models.Profile.objects.create()
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)

        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, username, password, **extra_fields)