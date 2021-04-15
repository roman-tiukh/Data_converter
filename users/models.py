from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from data_ocean.models import DataOceanModel
from users.validators import iban_validator, mfo_validator, name_symbols_validator, two_in_row_validator


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
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name']

    INDIVIDUAL = 'individual'
    INDIVIDUAL_ENTREPRENEUR = 'individual_entrepreneur'
    LEGAL_ENTITY = 'legal_entity'
    PERSON_STATUS = (
        (INDIVIDUAL, _('Individual')),
        (INDIVIDUAL_ENTREPRENEUR, _('Individual entrepreneur')),
        (LEGAL_ENTITY, _('Legal entity')),
    )

    first_name = models.CharField(max_length=150, validators=[
        name_symbols_validator,
        two_in_row_validator,
    ])
    last_name = models.CharField(max_length=150, validators=[
        name_symbols_validator,
        two_in_row_validator,
    ])
    email = models.EmailField(_('email address'), unique=True)
    organization = models.CharField(max_length=255, default='', blank=True)
    position = models.CharField(max_length=150, default='', blank=True)
    phone = models.CharField(max_length=16, default='', blank=True)
    date_of_birth = models.DateField(default=None, null=True, blank=True)
    language = models.CharField(
        _('language'),
        max_length=2,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        blank=True,
    )

    person_status = models.CharField(choices=PERSON_STATUS, default=INDIVIDUAL, max_length=23, blank=True)
    iban = models.CharField('IBAN', max_length=29, default='', blank=True, validators=[iban_validator])
    company_name = models.CharField('Company name', max_length=300, default='', blank=True)
    company_address = models.CharField('Company registration address', max_length=150, default='', blank=True)
    identification_code = models.CharField('EDRPOU/ITN', max_length=10, default='', blank=True)
    mfo = models.CharField('MFO', max_length=6, default='', blank=True, validators=[mfo_validator])

    # Permissions
    datasets_admin = models.BooleanField(blank=True, default=False)
    users_viewer = models.BooleanField(blank=True, default=False)
    payment_system_admin = models.BooleanField(blank=True, default=False)

    objects = DataOceanUserManager()

    @property
    def invitations(self):
        from payment_system.models import Invitation
        return Invitation.objects.filter(
            email=self.email,
            deleted_at__isnull=True,
        )

    def notify(self, message: str, link: str = ''):
        self.notifications.create(
            message=message,
            link=link,
        )

    def get_alerts(self):
        """
        Calculate here list of alerts for user and return it
        alert structure = {
            'message': 'some message for user',
            'link': 'https://dataocean.us/',
        }
        """
        alerts = []
        active_p2s = self.user_projects.get(is_default=True).project.active_p2s
        if not active_p2s.subscription.is_default and active_p2s.latest_invoice \
                and not active_p2s.latest_invoice.is_paid:
            alerts.append({
                'message': _('You have not paid the invoice'),
                'link': f'{settings.FRONTEND_SITE_URL}/system/profile/my-payments/',
            })
        # alerts.append({
        #     'message': 'Lorem ipsum dolor sit amet, consectetur adipiscing eliуushte '
        #                'tortor imperdiet vuleputate pellentesque amet convallscscsis massa. '
        #                'Elementum ultrices poin enim id  elemencscscsctum.',
        #     'link': 'http://localhost:3000/system/profile/projects/'
        # })
        return alerts

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'


class CandidateUserModel(models.Model):
    email = models.EmailField(_('email address'), unique=True)
    password = models.CharField(_('password'), max_length=128)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    phone = models.CharField(max_length=16, default='', blank=True)
    language = models.CharField(
        _('language'),
        max_length=2,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        blank=True,
    )
    expire_at = models.DateTimeField(_('expire at'), null=True, blank=True)

    def __str__(self):
        return self.email


class Question(DataOceanModel):
    text = models.TextField('text', max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='questions')
    answered = models.BooleanField('was answered', default=False)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')


class Notification(DataOceanModel):
    user = models.ForeignKey(
        DataOceanUser, on_delete=models.CASCADE,
        related_name='notifications',
    )
    message = models.CharField(max_length=500)
    link = models.URLField(blank=True, default='')
    is_read = models.BooleanField(blank=True, default=False)

    def read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
