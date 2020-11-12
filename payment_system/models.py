from django.conf import settings
from django.db import models
from django.utils import timezone

from data_ocean.models import DataOceanModel
from data_ocean.utils import generate_key
from payment_system.constants import DEFAULT_SUBSCRIPTION_NAME


class UserProject(DataOceanModel):
    INITIATOR = 'initiator'
    PARTICIPANT = 'participant'
    ROLES = [
        (INITIATOR, 'Initiator'),
        (PARTICIPANT, 'Participant'),
    ]

    INVITED = 'invited'
    ACTIVE = 'active'
    REMOVED = 'removed'
    STATUSES = [
        (INVITED, 'Invited'),
        (ACTIVE, 'Active'),
        (REMOVED, "Removed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='user_projects')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='user_projects')
    role = models.CharField(choices=ROLES, max_length=20, default=PARTICIPANT, blank=True)
    status = models.CharField(choices=STATUSES, max_length=7, default=INVITED, blank=True)

    def __str__(self):
        return self.role

    class Meta:
        unique_together = [['user', 'project']]
        ordering = ['id']


class ProjectSubscription(DataOceanModel):
    ACTIVE = 'active'
    PAST = 'past'
    FUTURE = 'future'
    STATUSES = [
        (ACTIVE, 'Active'),
        (PAST, 'Past'),
        (FUTURE, 'Future'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                related_name='project_subscriptions')
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE,
                                     related_name='project_subscriptions')
    status = models.CharField(choices=STATUSES, max_length=10)
    expiring_date = models.DateField(null=True, blank=True)

    @classmethod
    def create(cls, project, subscription):
        current_project_subscription = ProjectSubscription.objects.filter(
            project=project,
            status=ProjectSubscription.ACTIVE
        ).first()
        if current_project_subscription.subscription.name == DEFAULT_SUBSCRIPTION_NAME:
            current_project_subscription.status = ProjectSubscription.PAST
            current_project_subscription.save()
            return ProjectSubscription.objects.create(
                project=project,
                subscription=subscription,
                status=ProjectSubscription.ACTIVE,
                expiring_date=timezone.localdate() + timezone.timedelta(days=30)
            )
        else:
            return ProjectSubscription.objects.create(
                project=project,
                subscription=subscription,
                status=ProjectSubscription.FUTURE,
                expiring_date=current_project_subscription.expiring_date + timezone.timedelta(days=30)
            )

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

    @classmethod
    def create(cls, initiator, name, description=''):
        try:
            default_subscription = Subscription.objects.get(name=DEFAULT_SUBSCRIPTION_NAME)
        except Subscription.DoesNotExist:
            raise Exception(f'Default subscription "{DEFAULT_SUBSCRIPTION_NAME}" not exists')

        new_project = Project.objects.create(
            name=name,
            token=generate_key(),
            description=description
        )
        new_project.user_projects.create(
            user=initiator,
            role=UserProject.INITIATOR,
            status=UserProject.ACTIVE,
        )
        new_project.add_default_subscription(default_subscription)
        return new_project

    def add_default_subscription(self) -> ProjectSubscription:
        return ProjectSubscription.objects.create(
            project=self,
            subscription=Subscription.objects.get(name=DEFAULT_SUBSCRIPTION_NAME),
            status=ProjectSubscription.ACTIVE,
            expiring_date=timezone.localdate() + timezone.timedelta(days=30)
        )

    def add_user(self, user):
        self.user_projects.create(user=user)
        # should I add sending email here?

    def confirm_invitation(self, user):
        user_project = self.user_projects.get(user=user)
        user_project.status = UserProject.ACTIVE
        user_project.save(update_fields=['status'])
        # should I add sending email here?

    def remove_user(self, user):
        user_project = self.user_projects.get(user=user)
        user_project.status = UserProject.REMOVED
        user_project.save(update_fields=['status'])
        # should I add sending email here?

    def disable(self):
        self.disabled_at = timezone.now()
        self.save(update_fields=['disabled_at'])

    def activate(self):
        self.disabled_at = None
        self.save(update_fields=['disabled_at'])

    @property
    def is_active(self):
        return self.disabled_at is None

    def refresh_token(self):
        self.token = generate_key()
        self.save(update_fields=['token'])

    def has_write_perms(self, user):
        u2p: UserProject = self.user_projects.get(user=user)
        return u2p.status == UserProject.ACTIVE and u2p.role == UserProject.INITIATOR


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
