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
    token = models.CharField(max_length=40, unique=True, db_index=True)
    disabled_at = models.DateTimeField(null=True, blank=True, default=None)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserProject',
                                   related_name='projects')
    subscriptions = models.ManyToManyField('Subscription', through='ProjectSubscription',
                                           related_name='projects')

    def save(self, *args, **kwargs):
        if not self.token:
            self.generate_new_token()
        super().save(*args, **kwargs)

    def generate_new_token(self):
        def get_token_safe():
            new_key = generate_key()
            if Project.objects.filter(token=new_key).exists():
                return get_token_safe()
            else:
                return new_key

        self.token = get_token_safe()

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
            is_default=True,
            defaults={
                'requests_limit': 1000,
                'name': settings.DEFAULT_SUBSCRIPTION_NAME,
            },
        )
        date_now = timezone.localdate()
        return ProjectSubscription.objects.create(
            project=self,
            subscription=default_subscription,
            status=ProjectSubscription.ACTIVE,
            start_date=date_now,
            expiring_date=date_now + timezone.timedelta(days=default_subscription.duration),
        )

    def invite_user(self, email: str):
        if self.user_projects.filter(user__email=email).exists():
            raise RestValidationError({'detail': 'User already in project'})

        if self.invitations.filter(email=email, deleted_at__isnull=True).exists():
            raise RestValidationError({'detail': 'User already invited'})

        invitation, created = Invitation.objects.get_or_create(
            email=email, project=self,
        )
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

    def deactivate_user(self, user_id):
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

    def refresh_token(self):
        self.generate_new_token()
        self.save(update_fields=['token'])

    def has_read_perms(self, user):
        u2p: UserProject = self.user_projects.get(user=user)
        return u2p.status == UserProject.ACTIVE

    def has_write_perms(self, user):
        u2p: UserProject = self.user_projects.get(user=user)
        return u2p.status == UserProject.ACTIVE and u2p.role == UserProject.OWNER

    def add_subscription(self, subscription: 'Subscription'):
        assert isinstance(subscription, Subscription)
        current_p2s = ProjectSubscription.objects.get(
            project=self,
            status=ProjectSubscription.ACTIVE,
        )
        if subscription.is_default:
            raise RestValidationError({
                'detail': 'Cant add default subscription.'
            })
        if ProjectSubscription.objects.filter(
            project=self,
            status=ProjectSubscription.FUTURE,
        ).exists():
            raise RestValidationError({
                'detail': 'Can\'t add second future subscription.'
            })

        if current_p2s.subscription.is_default:
            current_p2s.status = ProjectSubscription.PAST
            current_p2s.save()
            date_now = timezone.localdate()
            new_p2s = ProjectSubscription.objects.create(
                project=self,
                subscription=subscription,
                status=ProjectSubscription.ACTIVE,
                start_date=date_now,
                expiring_date=date_now + timezone.timedelta(days=subscription.grace_period),
                is_grace_period=True,
            )
        else:
            grace_period_used = self.project_subscriptions.filter(
                status=ProjectSubscription.PAST,
                subscription__is_default=False,
                is_grace_period=True,
            ).exists()
            if current_p2s.is_grace_period or grace_period_used:
                raise RestValidationError({
                    'detail': 'You have subscription on a grace period, cant add new subscription',
                })

            new_p2s = ProjectSubscription.objects.create(
                project=self,
                subscription=subscription,
                status=ProjectSubscription.FUTURE,
                start_date=current_p2s.expiring_date,
                expiring_date=(current_p2s.expiring_date +
                               timezone.timedelta(days=subscription.grace_period)),
                is_grace_period=True,
            )
        new_p2s.invoices.create()
        return new_p2s

    @property
    def is_active(self):
        return self.disabled_at is None

    @property
    def owner(self):
        return self.user_projects.get(
            role=UserProject.OWNER,
        ).user

    @property
    def active_subscription(self) -> 'Subscription':
        return self.active_p2s.subscription

    @property
    def active_p2s(self) -> 'ProjectSubscription':
        return self.project_subscriptions.get(status=ProjectSubscription.ACTIVE)


class Subscription(DataOceanModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, default='')
    price = models.SmallIntegerField(default=0)
    requests_limit = models.IntegerField(help_text='Limit for API requests from the project')
    duration = models.SmallIntegerField(default=30, help_text='days')
    grace_period = models.SmallIntegerField(default=10, help_text='days')
    is_custom = models.BooleanField(
        blank=True, default=False,
        help_text='Custom subscription not shown to users',
    )
    is_default = models.BooleanField(blank=True, default=False)

    @classmethod
    def get_default_subscription(cls):
        return cls.objects.get(is_default=True)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        # check only one default subscription
        if self.is_default:
            exists = Subscription.objects.filter(is_default=True).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError('Default subscription already exists')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['price']


class Invoice(DataOceanModel):
    paid_at = models.DateField(
        null=True, blank=True,
        help_text='This operation is irreversible, you cannot '
                  'cancel the payment of the subscription for the project.'
    )
    project_subscription = models.OneToOneField(
        'ProjectSubscription', on_delete=models.PROTECT,
        related_name='invoice',
    )
    note = models.CharField(max_length=500, blank=True, default='')
    disable_grace_period_block = models.BooleanField(
        blank=True, default=False,
        help_text='If set to True, then the user will be allowed '
                  'to use "grace period" again, the opportunity to pay will be lost'
    )

    @property
    def is_paid(self):
        return bool(self.paid_at)

    def save(self, *args, **kwargs):
        if getattr(self, 'id', False):
            p2s = self.project_subscription
            invoice_old = Invoice.objects.get(pk=self.pk)
            if p2s.is_grace_period and not invoice_old.is_paid and self.is_paid:
                p2s.paid_up()
            else:
                if self.disable_grace_period_block and not invoice_old.disable_grace_period_block:
                    p2s.is_grace_period = False
                    p2s.save()
                elif not self.disable_grace_period_block and invoice_old.disable_grace_period_block:
                    p2s.is_grace_period = True
                    p2s.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Invoice #{self.id}'


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

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        # Validate only one default project
        if self.is_default:
            default_count = UserProject.objects.filter(
                user=self.user, is_default=True,
            ).exclude(id=self.id).count()
            if default_count:
                raise ValidationError('User can only have one default project')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Project {self.project.name} of user {self.user.get_full_name()}'

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

    status = models.CharField(choices=STATUSES, max_length=10, db_index=True)

    start_date = models.DateField()
    expiring_date = models.DateField()
    is_grace_period = models.BooleanField(blank=True, default=True)

    requests_left = models.IntegerField()
    requests_used = models.IntegerField(blank=True, default=0)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        def check_unique_status(status):
            if self.status == status:
                is_exists = ProjectSubscription.objects.filter(
                    project=self.project,
                    status=status,
                ).exclude(pk=self.pk).exists()
                if is_exists:
                    raise ValidationError({
                        'detail': f'Only one {status} subscription in project',
                    })

        check_unique_status(ProjectSubscription.ACTIVE)
        check_unique_status(ProjectSubscription.FUTURE)

    def paid_up(self):
        assert self.is_grace_period
        date_now = timezone.localdate()
        used_grace_days = 0
        if self.start_date < date_now:
            used_grace_days = (date_now - self.start_date).days
        days_left = self.subscription.duration - used_grace_days
        self.expiring_date += timezone.timedelta(days=days_left)
        self.is_grace_period = False
        self.save()

    def disable(self):
        self.status = ProjectSubscription.PAST
        self.expiring_date = None
        self.save()

    def expire(self):
        try:
            next_p2s = ProjectSubscription.objects.get(
                project=self.project,
                status=ProjectSubscription.FUTURE,
            )
        except ProjectSubscription.DoesNotExist:
            if self.subscription.is_default:
                self.expiring_date += timezone.timedelta(days=self.subscription.duration)
                self.save()
            else:
                self.status = ProjectSubscription.PAST
                self.save()
                self.project.add_default_subscription()
        else:
            self.status = ProjectSubscription.PAST
            self.save()
            next_p2s.status = ProjectSubscription.ACTIVE
            next_p2s.save()

    @classmethod
    def update_expire_subscriptions(cls) -> str:
        project_subscriptions_for_update = ProjectSubscription.objects.filter(
            expiring_date__lte=timezone.localdate(),
            status=ProjectSubscription.ACTIVE,
        )

        if not project_subscriptions_for_update:
            return 'No project_subscriptions to update'

        i = 0
        for current_p2s in project_subscriptions_for_update:
            current_p2s.expire()
            i += 1
        return f'Success! {i} subscriptions updated'

    def save(self, *args, **kwargs):
        if not getattr(self, 'id', None):
            self.requests_left = self.subscription.requests_limit
        self.validate_unique()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.project.owner.get_full_name()} | {self.project.name} | {self.subscription}'

    class Meta:
        verbose_name = "relation between the project and its subscriptions"
        ordering = ['-created_at']


class Invitation(DataOceanModel):
    email = models.EmailField()
    project = models.ForeignKey('Project', models.CASCADE, related_name='invitations')

    # who_invited = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE,
    #                                 related_name='who_invitations')

    class Meta:
        unique_together = [['email', 'project']]
