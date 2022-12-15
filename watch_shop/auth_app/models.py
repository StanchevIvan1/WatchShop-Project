from django.contrib.auth import models as auth_models
from django.db import models

from watch_shop.auth_app.managers import AppUserManager


class AppUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
    )

    is_staff = models.BooleanField(
        default=False,
        null=False,
        blank=False,
    )

    # User Credentials consist of 'email' and password
    USERNAME_FIELD = 'email'

    object = AppUserManager()


class Profile(models.Model):
    first_name = models.CharField(
        max_length=25,
        blank=True,
        null=True,
    )

    last_name = models.CharField(
        max_length=25,
        blank=True,
        null=True,
    )

    age = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    photo = models.ImageField(
        upload_to='images',
        default='blank_profile_image.jpeg',
    )

    user = models.OneToOneField(
        AppUser,
        primary_key=True,
        on_delete=models.CASCADE,
    )
