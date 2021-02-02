import io
import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext, gettext_lazy as _
from weasyprint import HTML

from data_ocean.models import DataOceanModel
from data_ocean.utils import generate_key

from payment_system import emails


class Project(DataOceanModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, default='')
    token = models.CharField(max_length=40, unique=True, db_index=True)
    disabled_at = models.DateTimeField(null=True, blank=True, default=None)
    owner = models.ForeignKey('users.DataOceanUser', models.CASCADE, related_name='owned_projects')
    users = models.ManyToManyField('users.DataOceanUser', through='UserProject',
                                   related_name='projects')
    subscriptions = models.ManyToManyField('Subscription', through='ProjectSubscription',
                                           related_name='projects')

    @property
    def frontend_projects_link(self):
        return f'{settings.FRONTEND_SITE_URL}/system/profile/projects/'

    @property
    def frontend_link(self):
        return f'{self.frontend_projects_link}{self.id}/'

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
            description=description,
            owner=owner,
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
                'grace_period': 30,
            },
        )
        date_now = timezone.localdate()
        return ProjectSubscription.objects.create(
            project=self,
            subscription=default_subscription,
            status=ProjectSubscription.ACTIVE,
            start_date=date_now,
            duration=default_subscription.duration,
            grace_period=default_subscription.grace_period,
            expiring_date=date_now + timezone.timedelta(days=default_subscription.duration),
        )

    def invite_user(self, email: str):
        if self.user_projects.filter(user__email=email).exists():
            raise ValidationError(_('User already in project'))

        if self.invitations.filter(email=email, deleted_at__isnull=True).exists():
            raise ValidationError(_('User already invited'))

        invitation, created = Invitation.objects.get_or_create(
            email=email, project=self,
        )
        if not created:
            invitation.deleted_at = None
            invitation.save(update_fields=['deleted_at', 'updated_at'])

        emails.new_invitation(email, self)

    def _check_user_invitation(self, user):
        try:
            invitation = self.invitations.get(
                email=user.email, deleted_at__isnull=True,
            )
        except Invitation.DoesNotExist:
            raise ValidationError(_('User is not invited'))
        return invitation

    def reject_invitation(self, user):
        invitation = self._check_user_invitation(user)
        invitation.soft_delete()

    def confirm_invitation(self, user):
        invitation = self._check_user_invitation(user)

        if user in self.users.all():
            raise ValidationError(_('User already in project'))

        self.user_projects.create(
            user=user,
            role=UserProject.MEMBER,
            status=UserProject.ACTIVE,
        )
        invitation.soft_delete()
        emails.membership_confirmed(self.owner, user)

    def deactivate_user(self, user_id):
        u2p = self.user_projects.get(user_id=user_id)
        if u2p.role == UserProject.OWNER:
            raise ValidationError(_('You cannot deactivate an owner from his own project'))
        if u2p.status == UserProject.DEACTIVATED:
            raise ValidationError(_('User already deactivated'))
        u2p.status = UserProject.DEACTIVATED
        u2p.save(update_fields=['status', 'updated_at'])
        emails.member_removed(u2p.user, self)

    def activate_user(self, user_id):
        u2p = self.user_projects.get(user_id=user_id)
        if u2p.status == UserProject.ACTIVE:
            raise ValidationError(_('User already activated'))
        u2p.status = UserProject.ACTIVE
        u2p.save(update_fields=['status', 'updated_at'])
        emails.member_activated(u2p.user, self)

    def disable(self):
        for u2p in self.user_projects.all():
            if u2p.is_default:
                raise ValidationError(_('You cannot disable default project'))

        self.disabled_at = timezone.now()
        self.save(update_fields=['disabled_at', 'updated_at'])

    def activate(self):
        self.disabled_at = None
        self.save(update_fields=['disabled_at', 'updated_at'])

    def refresh_token(self):
        self.generate_new_token()
        self.save(update_fields=['token', 'updated_at'])
        emails.token_has_been_changed(self)

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
        # if subscription.is_default:
        #     raise ValidationError(_('Can\'t add default subscription'))
        if ProjectSubscription.objects.filter(
                project=self,
                status=ProjectSubscription.FUTURE,
        ).exists():
            raise ValidationError(_('Can\'t add second future subscription'))

        grace_period_used = []
        for project in self.owner.owned_projects.all():
            grace_period_used.append(
                project.project_subscriptions.filter(
                    subscription__is_default=False,
                    invoices__grace_period_block=True,
                ).exists()
            )
        if any(grace_period_used):
            raise ValidationError(_('Project have subscription on a grace period, cant add new subscription'))

        if current_p2s.subscription == subscription:
            raise ValidationError(gettext('Project already on {}').format(subscription.name))

        if current_p2s.subscription.is_default:
            current_p2s.status = ProjectSubscription.PAST
            current_p2s.save()
            date_now = timezone.localdate()
            new_p2s = ProjectSubscription.objects.create(
                project=self,
                subscription=subscription,
                status=ProjectSubscription.ACTIVE,
                start_date=date_now,
                duration=subscription.duration,
                grace_period=subscription.grace_period,
                expiring_date=date_now + timezone.timedelta(days=subscription.grace_period),
                is_grace_period=True,
            )
            Invoice.objects.create(project_subscription=new_p2s)
        else:
            if current_p2s.is_grace_period:
                raise ValidationError(_('Project have subscription on a grace period, can\'t add new subscription'))

            if subscription.is_default:
                duration = subscription.duration
            else:
                duration = subscription.grace_period

            new_p2s = ProjectSubscription.objects.create(
                project=self,
                subscription=subscription,
                status=ProjectSubscription.FUTURE,
                start_date=current_p2s.expiring_date,
                duration=subscription.duration,
                grace_period=subscription.grace_period,
                expiring_date=(current_p2s.expiring_date +
                               timezone.timedelta(days=duration)),
                is_grace_period=True,
            )
        emails.new_subscription(new_p2s)
        return new_p2s

    def remove_future_subscription(self):
        try:
            future_p2s = self.project_subscriptions.get(status=ProjectSubscription.FUTURE)
        except ProjectSubscription.DoesNotExist:
            raise ValidationError(_('Project don\'t have future subscription'))
        future_p2s.delete()

    @property
    def is_active(self):
        return self.disabled_at is None

    # @property
    # def owner(self):
    #     return self.user_projects.get(
    #         role=UserProject.OWNER,
    #     ).user

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
                raise ValidationError(_('Default subscription already exists'))

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
    token = models.UUIDField(db_index=True, default=uuid.uuid4, blank=True)

    project_subscription = models.ForeignKey(
        'ProjectSubscription', on_delete=models.PROTECT,
        related_name='invoices',
    )
    grace_period_block = models.BooleanField(
        blank=True, default=True,
        help_text='If set to False, then the user will be allowed '
                  'to use "grace period" again, the opportunity to pay will be lost'
    )
    note = models.TextField(blank=True, default='')

    # information about payment
    start_date = models.DateField()
    end_date = models.DateField()
    requests_limit = models.IntegerField()
    subscription_name = models.CharField(max_length=200)
    project_name = models.CharField(max_length=100)
    is_custom_subscription = models.BooleanField()

    price = models.IntegerField()

    @property
    def link(self):
        return reverse('payment_system:invoice_pdf', args=[self.id, self.token])

    @property
    def is_paid(self):
        return bool(self.paid_at)

    @property
    def tax(self):
        # if not self.price:
        #     return 0
        # return round(self.price * 0.2, 2)
        return 0

    @property
    def price_with_tax(self):
        # if not self.price:
        #     return 0
        # return round(self.price + self.tax, 2)
        return self.price

    @property
    def grace_period_end_date(self):
        return self.start_date + timezone.timedelta(days=self.project_subscription.grace_period)

    def save(self, *args, **kwargs):
        p2s = self.project_subscription
        if getattr(self, 'id', False):
            invoice_old = Invoice.objects.get(pk=self.pk)
            if p2s.is_grace_period and not invoice_old.is_paid and self.is_paid:
                p2s.paid_up()
                self.grace_period_block = False
                emails.payment_confirmed(p2s)
            # else:
            #     if self.grace_period_block and not invoice_old.grace_period_block:
            #         p2s.is_grace_period = False
            #         p2s.save()
            #     elif not self.disable_grace_period_block and invoice_old.disable_grace_period_block:
            #         p2s.is_grace_period = True
            #         p2s.save()
            super().save(*args, **kwargs)
        else:
            self.start_date = p2s.start_date
            self.end_date = p2s.start_date + timezone.timedelta(days=p2s.duration)
            self.requests_limit = p2s.subscription.requests_limit
            self.subscription_name = p2s.subscription.name
            self.project_name = p2s.project.name
            self.price = p2s.subscription.price
            self.is_custom_subscription = p2s.subscription.is_custom
            super().save(*args, **kwargs)
            emails.new_invoice(self, p2s.project)

    def get_pdf(self) -> io.BytesIO:
        user = self.project_subscription.project.owner

        with translation.override('uk'):
            html_string = render_to_string('payment_system/invoice.html', {
                'invoice': self,
                'user': user,
            })

        html = HTML(string=html_string, base_url=os.path.join(settings.BASE_DIR, 'payment_system'))
        result = html.write_pdf()
        file = io.BytesIO(result)
        file.name = 'Invoice from ' + str(self.created_at) + '.pdf'
        file.seek(0)
        return file

    def __str__(self):
        return f'Invoice #{self.id}'

    class Meta:
        ordering = ['-created_at']


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

    user = models.ForeignKey('users.DataOceanUser', on_delete=models.CASCADE,
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
                raise ValidationError(_('User can only have one default project'))

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'User {self.user.get_full_name()} in Project {self.project.name}'

    class Meta:
        unique_together = [['user', 'project']]
        ordering = ['id']


class ProjectSubscription(DataOceanModel):
    ACTIVE = 'active'
    PAST = 'past'
    FUTURE = 'future'
    STATUSES = (
        (ACTIVE, _('Active')),
        (PAST, _('Past')),
        (FUTURE, _('Future')),
    )
    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                related_name='project_subscriptions')
    subscription = models.ForeignKey('Subscription', on_delete=models.PROTECT,
                                     related_name='project_subscriptions')

    status = models.CharField(choices=STATUSES, max_length=10, db_index=True)

    start_date = models.DateField()
    expiring_date = models.DateField()
    is_grace_period = models.BooleanField(blank=True, default=True)

    requests_left = models.IntegerField()
    requests_used = models.IntegerField(blank=True, default=0)

    duration = models.SmallIntegerField(help_text='days')
    grace_period = models.SmallIntegerField(help_text='days')

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        def check_unique_status(status):
            if self.status == status:
                is_exists = ProjectSubscription.objects.filter(
                    project=self.project,
                    status=status,
                ).exclude(pk=self.pk).exists()
                if is_exists:
                    for code, verbose in self.STATUSES:
                        if code == status:
                            status = verbose
                            break
                    raise ValidationError(gettext('Only one {} subscription in project').format(status))

        check_unique_status(ProjectSubscription.ACTIVE)
        check_unique_status(ProjectSubscription.FUTURE)

    @property
    def payment_date(self):
        if self.is_grace_period:
            return self.start_date
        return self.expiring_date

    @property
    def payment_overdue_days(self):
        if self.is_grace_period and self.status == ProjectSubscription.ACTIVE:
            return (timezone.localdate() - self.start_date).days
        return None

    @property
    def is_paid(self):
        last_invoice = self.invoices.order_by('-created_at').first()
        return last_invoice and last_invoice.is_paid

    def paid_up(self):
        assert self.is_grace_period
        date_now = timezone.localdate()
        used_grace_days = 0
        if date_now > self.start_date:
            used_grace_days = (date_now - self.start_date).days

        if date_now >= self.expiring_date:
            used_grace_days = self.grace_period
        days_left = self.duration - used_grace_days
        self.expiring_date = date_now + timezone.timedelta(days=days_left)
        self.is_grace_period = False
        self.save()

    def disable(self):
        self.status = ProjectSubscription.PAST
        self.expiring_date = None
        self.save()

    def reset(self):
        self.is_grace_period = True
        self.requests_left = self.subscription.requests_limit
        self.requests_used = 0
        self.duration = self.subscription.duration
        self.grace_period = self.subscription.grace_period
        self.start_date = self.expiring_date

        if self.subscription.is_default:
            self.expiring_date += timezone.timedelta(days=self.duration)
        else:
            self.expiring_date += timezone.timedelta(days=self.grace_period)

    def expire(self):
        try:
            future_p2s = ProjectSubscription.objects.get(
                project=self.project,
                status=ProjectSubscription.FUTURE,
            )
        except ProjectSubscription.DoesNotExist:
            if self.subscription.is_default:
                self.reset()
                self.save()
            else:
                if self.is_grace_period:
                    self.status = ProjectSubscription.PAST
                    self.save()
                    self.project.add_default_subscription()
                    emails.project_non_payment(self.project)
                else:
                    self.reset()
                    self.save()
                    Invoice.objects.create(project_subscription=self)
        else:
            self.status = ProjectSubscription.PAST
            self.save()
            future_p2s.status = ProjectSubscription.ACTIVE
            future_p2s.save()
            if not future_p2s.subscription.is_default:
                Invoice.objects.create(project_subscription=future_p2s)

    @classmethod
    def send_tomorrow_payment_emails(cls):
        project_subscriptions_for_update = cls.objects.filter(
            expiring_date=timezone.localdate() + timezone.timedelta(days=2),
            status=ProjectSubscription.ACTIVE,
            is_grace_period=True,
            subscription__is_default=False,
        )
        for p2s in project_subscriptions_for_update:
            emails.tomorrow_payment_day(p2s)

    @classmethod
    def update_expire_subscriptions(cls) -> str:
        cls.send_tomorrow_payment_emails()
        project_subscriptions_for_update = cls.objects.filter(
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

    @property
    def latest_invoice(self) -> Invoice:
        return self.invoices.order_by('-created_at').first()

    def __str__(self):
        return f'{self.project.owner} | {self.project.name} | {self.subscription}'

    class Meta:
        verbose_name = "relation between the project and its subscriptions"
        ordering = ['-created_at']


class Invitation(DataOceanModel):
    email = models.EmailField()
    project = models.ForeignKey('Project', models.CASCADE, related_name='invitations')

    # who_invited = models.ForeignKey('users.DataOceanUser', models.CASCADE,
    #                                 related_name='who_invitations')

    class Meta:
        unique_together = [['email', 'project']]
