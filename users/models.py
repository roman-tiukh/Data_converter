from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import requests


class DataOceanUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
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
        return self.create_user(email, password, **extra_fields)


class DataOceanUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    organization = models.CharField(max_length=255, default='', blank=True)
    position = models.CharField(max_length=150, default='', blank=True)
    date_of_birth = models.DateField(default=None, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name']

    objects = DataOceanUserManager()

    def __str__(self):
        return self.email

    def send_registration_email(self):
        header_obj = {
            'Content-Type': 'application/json',
            'Authorisation': settings.POSTMAN_TOKEN,
            }
        data_obj = {
            "recipient": self.email,
            "text": self.first_name + ", ми отримали запит на реєстрацію у системі Data Ocean.",
            "subject": "Підтвердження реєстрації на Data Ocean"
            }
        return requests.post(settings.POSTMAN_URL, data=data_obj, headers=header_obj)
