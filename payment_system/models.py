from django.conf import settings
from django.db import models
from django.utils import timezone

from data_ocean.models import DataOceanModel


class ProjectSubscription(DataOceanModel):
    STATUSES = [
        ('active', 'active'),
        ('past', 'past'),
        ('future', 'future'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='project_subscriptions')
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE,
                                     related_name='project_subscriptions')
    status = models.CharField(choices=STATUSES, max_length=10)
    expiring_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "relation between the project and its subscriptions"


class Project(DataOceanModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, default='')
    token = models.CharField(max_length=40, unique=True)
    disabled_at = models.DateTimeField(null=True, blank=True, default=None)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projects')
    subscriptions = models.ManyToManyField('Subscription', through=ProjectSubscription,
                                           related_name='projects')

    def add_user(self, user):
        self.users.add(user)

    def remove_user(self, user):
        self.users.remove(user)

    def disable(self):
        self.disabled_at = timezone.now()
        self.save(update_fields=['disabled_at'])

    def activate(self):
        self.disabled_at = None
        self.save(update_fields=['disabled_at'])

    @property
    def is_active(self):
        return self.disabled_at is None


class Subscription(DataOceanModel):
    custom = models.BooleanField(blank=True, default=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    price = models.SmallIntegerField(blank=True, default=0)
    requests_limit = models.IntegerField('limit for API requests from the project')
    duration = models.SmallIntegerField(blank=True, default=30)
    grace_period = models.SmallIntegerField(blank=True, default=30)


class Invoice(DataOceanModel):
    paid_at = models.DateField(null=True, blank=True)
    # this field is for an accountant`s notes
    info = models.CharField(max_length=500, blank=True, default='')
    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                related_name='project_invoices')
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE,
                                     related_name='subscription_invoices')
