from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password1=None, password2=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not full_name:
            raise ValueError("Users must have an full name address")

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
        )

        user.set_password(password1)
        user.set_password(password2)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **other_fields):
        user = self.create_user(email,password=password,full_name=full_name)
        other_fields.setdefault('is_admin', True)
        other_fields.setdefault('is_active', True)
        user.save(using=self._db)
        return user
