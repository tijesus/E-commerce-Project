from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Model manager for CustomUser
    """
    def create_user(self, email, first_name, last_name, phone, password=None, **extra_fields):
        """
        Create and return a regular user with an email, first name, last name, and phone number.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone, password=None, **extra_fields):
        """
        Create and return a superuser with an email, first name, last name, and phone number.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, phone, password, **extra_fields)



class User(AbstractUser):
    """
    CustomUser model.
    """
    username = None
    USERNAME_FIELD = "email"
    date_joined = None
    REQUIRED_FIELDS = ["first_name", "last_name", "phone"]

    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True, error_messages={
        "unique": "A user with that email already exists.",
    })
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=10, unique=True, error_messages={
        "unique": "A user with that phone already exists.",
    })
    is_active = models.BooleanField(default=False)
    password = models.CharField(max_length=128)

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        """
        Overrides the default save method.
        """
        self.email = self.email.lower()  # Ensure email is saved in lowercase
        self.phone = '0' + self.phone if len(self.phone) == 10 else self.phone
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()
