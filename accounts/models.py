from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django.utils import timezone


def get_upload_to(self, filename):
    return f"{self.email}/profile/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    start_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    image = models.ImageField(upload_to=get_upload_to, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin