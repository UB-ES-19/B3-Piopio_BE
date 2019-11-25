from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from piopio_be import models


class PiopioUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create(self, email, username, password, profile, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('Email address is required.')
        if not username:
            raise ValueError('Username is required.')
        if not profile:
            raise ValueError('Profile is required.')

        # Create and save User
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save()
        # Create and save Profile
        profile = models.Profile(
            first_name=profile.get('first_name'),
            last_name=profile.get('last_name'),
            user=user
        )
        profile.save()
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
        return self.create(email, username, password, **extra_fields)
