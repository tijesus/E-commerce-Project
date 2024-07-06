"""
Classes: CustomUserManager()
         User()
         Address()
"""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import BaseUserManager
from uuid import uuid4, UUID



phone_regex = RegexValidator(
        r'^0\d{10}$',
        message="Enter a valid Nigerian number",
        code="Invalid_phone"
        )

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

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=11, unique=True, validators=[phone_regex])
    is_active = models.BooleanField(default=False)
    password = models.CharField(max_length=128)

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        """
        Overrides the default save method.
        """
        self.email = self.email.lower()  # Ensure email is saved in lowercase
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()

    def get_cart_items(self) ->QuerySet:
        """
        gets all the items in a user's cart
        """
        ...
    def get_orders(self) -> QuerySet:
        """
        gets all the orders a user has made
        """
        ...

    def orderedAndDeliverd(self, product_id: UUID) -> bool:
        """
        checks if a user has ordered a particular product
        and the product has been delivered
        """
        ...

    def has_reviewed(self, product_id: UUID) -> bool:
        ...





class Address(models.Model):
    """
    Address model.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='address')
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    state = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255,
                                blank=True,
                                null=True,
                                help_text="Optional landmark near the address")
    description = models.TextField(blank=True,
                                   null=True,
                                   help_text="Additional description or notes about the address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address

    def has_landmark(self):
        """
        Checks if the address has a landmark
        """
        return True if self.landmark else False

    def has_description(self):
        """
        Checks if the address has a description
        """
        return True if self.description else False