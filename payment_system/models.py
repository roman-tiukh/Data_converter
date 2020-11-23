from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError as RestValidationError

from data_ocean.models import DataOceanModel
from data_ocean.utils import generate_key


class Project(DataOceanModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, default='')
    token = models.CharField(max_length=40, unique=True)
    disabled_at = models.DateTimeField(null=True, blank=True, default=None)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserProject',
                                   related_name='projects')
    subscriptions = models.ManyToManyField('Subscription', through='ProjectSubscription',
                                           related_name='projects')

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = generate_key()
        super().save(*args, **kwargs)

    @classmethod
    def create(cls, owner, name, description='', is_default=False):
        new_project = Project.objects.create(
            name=name,
            description=description
        )
        new_project.user_projects.create(
            user=owner,
            role=UserProject.OWNER,
            status=UserProject.ACTIVE,
            is_default=is_default,
        )
        new_project.add_default_subscription()
        return new_project

    def add_default_subscription(self) -> 'ProjectSubscription':
        default_subscription, created = Subscription.objects.get_or_create(
            name=settings.DEFAULT_SUBSCRIPTION_NAME,
            defaults={'requests_limit': 1000},
        )
        return ProjectSubscription.objects.create(
            project=self,
            subscription=default_subscription,
            status=ProjectSubscription.ACTIVE,
            expiring_date=timezone.localdate() + timezone.timedelta(days=30)
        )

    def invite_user(self, email: str):
        if self.user_projects.filter(user__email=email).exists():
            raise RestValidationError({'detail': 'User already in project'})

        if self.invitations.filter(email=email, deleted_at__isnull=True).exists():
            raise RestValidationError({'detail': 'User already invited'})

        invitation, created = self.invitations.get_or_create(email=email)
        if not created:
            invitation.deleted_at = None
            invitation.save(update_fields=['deleted_at'])

        print(f'EMAIL: user {email} invited')

    def _check_user_invitation(self, user):
        try:
            invitation = self.invitations.get(
                email=user.email, deleted_at__isnull=True,
            )
        except Invitation.DoesNotExist:
            raise RestValidationError({'detail': 'User is not invited'})
        return invitation

    def reject_invitation(self, user):
        invitation = self._check_user_invitation(user)
        invitation.soft_delete()

    def confirm_invitation(self, user):
        invitation = self._check_user_invitation(user)

        if user in self.users.all():
            raise RestValidationError({'detail': 'User already in project'})

        self.user_projects.create(
            user=user,
            role=UserProject.MEMBER,
            status=UserProject.ACTIVE,
        )
        invitation.soft_delete()

    def remove_user(self, user_id):
        u2p = self.user_projects.get(user_id=user_id)
        if u2p.role == UserProject.OWNER:
            raise RestValidationError({'detail': 'You cannot deactivate an owner from his own project'})
        if u2p.status == UserProject.DEACTIVATED:
            raise RestValidationError({'detail': 'User already deactivated'})
        u2p.status = UserProject.DEACTIVATED
        u2p.save(update_fields=['status'])

    def activate_user(self, user_id):
        u2p = self.user_projects.get(user_id=user_id)
        if u2p.status == UserProject.ACTIVE:
            raise RestValidationError({'detail': 'User already activated'})
        u2p.status = UserProject.ACTIVE
        u2p.save(update_fields=['status'])
        # should I add sending email here?

    def disable(self):
        for u2p in self.user_projects.all():
            if u2p.is_default:
                raise RestValidationError({
                    'detail': 'You cannot disable default project',
                })

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

    def has_read_perms(self, user):
        u2p: UserProject = self.user_projects.get(user=user)
        return u2p.status == UserProject.ACTIVE

    def has_write_perms(self, user):
        u2p: UserProject = self.user_projects.get(user=user)
        return u2p.status == UserProject.ACTIVE and u2p.role == UserProject.OWNER

    @property
    def owner(self):
        return self.user_projects.get(
            role=UserProject.OWNER,
        ).user


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


class UserProject(DataOceanModel):
    OWNER = 'owner'
    MEMBER = 'member'
    ROLES = (
        (OWNER, 'Owner'),
        (MEMBER, 'Member'),
    )

    ACTIVE = 'active'
    DEACTIVATED = 'deactivated'
    STATUSES = (
        (ACTIVE, 'Active'),
        (DEACTIVATED, "Deactivated"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='user_projects')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='user_projects')
    role = models.CharField(choices=ROLES, max_length=20)
    status = models.CharField(choices=STATUSES, max_length=11)
    is_default = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return self.role

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        # Validate only one default project
        if self.is_default:
            default_count = UserProject.objects.filter(
                user=self.user, is_default=True,
            ).exclude(id=self.id).count()
            if default_count:
                raise ValidationError('User can only have one default project')

    class Meta:
        unique_together = [['user', 'project']]
        ordering = ['id']


class ProjectSubscription(DataOceanModel):
    ACTIVE = 'active'
    PAST = 'past'
    FUTURE = 'future'
    STATUSES = (
        (ACTIVE, 'Active'),
        (PAST, 'Past'),
        (FUTURE, 'Future'),
    )
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
        if current_project_subscription.subscription.name == settings.DEFAULT_SUBSCRIPTION_NAME:
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


class Invitation(DataOceanModel):
    email = models.EmailField()
    project = models.ForeignKey('Project', models.CASCADE, related_name='invitations')
    # who_invited = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE,
    #                                 related_name='who_invitations')

    class Meta:
        unique_together = [['email', 'project']]
