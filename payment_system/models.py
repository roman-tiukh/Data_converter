from django.conf import settings
from django.db import models
from django.utils import timezone

from data_ocean.models import DataOceanModel


class UserProject(DataOceanModel):
    INITIATOR = 'initiator'
    PARTICIPANT = 'participant'
    ROLES = [
        (INITIATOR, 'Initiator'),
        (PARTICIPANT, 'Participant'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='user_projects')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='user_projects')
    role = models.CharField(choices=ROLES, max_length=20, default=PARTICIPANT, blank=True)

    def __str__(self):
        return self.role


class ProjectSubscription(DataOceanModel):
    ACTIVE = 'active'
    PAST = 'past'
    FUTURE = 'future'
    STATUSES = [
        (ACTIVE, 'active'),
        (PAST, 'past'),
        (FUTURE, 'future'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                related_name='project_subscriptions')
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE,
                                     related_name='project_subscriptions')
    status = models.CharField(choices=STATUSES, max_length=10)
    expiring_date = models.DateField(null=True, blank=True)

    @classmethod
    def create(cls, project, subscription):
        project_subscription = ProjectSubscription.objects.filter(
            project=project,
            subscription=subscription,
            status=ProjectSubscription.ACTIVE
        ).first()
        if not project_subscription:
            return ProjectSubscription.objects.create(
                project=project,
                subscription=subscription,
                status=ProjectSubscription.ACTIVE,
                expiring_date=timezone.localdate() + timezone.timedelta(days=30)
            )
        return project_subscription

    def disable(self):
        self.status = ProjectSubscription.PAST
        self.expiring_date = None
        self.save()

    class Meta:
        verbose_name = "relation between the project and its subscriptions"


class Project(DataOceanModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, default='')
    token = models.CharField(max_length=40, unique=True)
    disabled_at = models.DateTimeField(null=True, blank=True, default=None)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through=UserProject,
                                   related_name='projects')
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

    def __str__(self):
        return f'Invoice N{self.id}'
