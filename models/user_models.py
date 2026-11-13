from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from models.base_models import BaseModel
from django.utils.timezone import now
from datetime import timedelta
from django.utils.text import slugify
from helpers.translation import register_key

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class UserManager(BaseUserManager):

    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("You must provide a valid email")

    def create_user(self, email, username=None, password=None, **extra_fields):

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError("Base User: and email address is required")

        user = self.model(username=username, email=email, **extra_fields)

        user.set_password(password)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user.save()

        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusers must have is_superuser=True")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusers must have is_staff=True")

        if not password:
            raise ValueError("Superusers must have a password")

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError("Admin User: and email address is required")

        user = self.create_user(email, username, password, **extra_fields)

        user.save()

        return user


class UserModel(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(
        "core.RoleModel", on_delete=models.SET_NULL, null=True, blank=True
    )
    phone = models.CharField(max_length=50, null=True, blank=True)
    profile = models.ImageField(upload_to="profile", null=True, blank=True)
    gem = models.PositiveIntegerField(default=0)
    free_gem = models.PositiveIntegerField(default=0)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_developer = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        app_label = "core"
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        key = slugify(self.username).replace("-", "_").lower()
        register_key(key, self.username)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.username).replace("-", "_").lower()

    def has_permission(self, perm_codename):
        if self.is_superuser:
            return True
        return (
            self.role and self.role.permissions.filter(codename=perm_codename).exists()
        )

    def has_module_perms(self, app_label):
        return (
            self.role
            and self.role.permissions.filter(content_type__app_label=app_label).exists()
        )

    def get_all_permission_ids(self):
        role_perms = set()
        if self.role:
            role_perms = set(self.role.permissions.values_list("id", flat=True))
            user_perms = set(self.user_permissions.values_list("id", flat=True))
            return role_perms.union(user_perms)

    def is_online(self):
        return self.last_active >= now() - timedelta(minutes=5)
