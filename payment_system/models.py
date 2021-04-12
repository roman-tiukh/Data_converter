import io
import os
import uuid
from calendar import monthrange

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
from users.validators import name_symbols_validator, two_in_row_validator


class Project(DataOceanModel):
    name = models.CharField(_('name'), max_length=50)
    description = models.CharField(max_length=500, blank=True, default='')
    token = models.CharField(max_length=40, unique=True, db_index=True)
    disabled_at = models.DateTimeField(_('disabled_at'), null=True, blank=True, default=None)
    owner = models.ForeignKey('users.DataOceanUser', models.CASCADE,
                              related_name='owned_projects', verbose_name=_('owner'))
    users = models.ManyToManyField('users.DataOceanUser', through='UserProject',
                                   related_name='projects', verbose_name=_('user'))
    subscriptions = models.ManyToManyField('Subscription', through='ProjectSubscription',
                                           related_name='projects',
                                           verbose_name=_('subscriptions'))

    @property
    def frontend_projects_link(self):
        return f'{settings.FRONTEND_SITE_URL}/system/profile/projects/'

    @property
    def frontend_link(self):
        return f'{self.frontend_projects_link}{self.id}/'

    @property
    def is_disabled(self):
        return bool(self.disabled_at)

    def __str__(self):
        return f'{self.name} of {self.owner}'

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
                'requests_limit': 20,
                'platform_requests_limit': 200,
                'name': settings.DEFAULT_SUBSCRIPTION_NAME,
                'grace_period': 30,
            },
        )
        return ProjectSubscription.objects.create(
            project=self,
            subscription=default_subscription,
            status=ProjectSubscription.ACTIVE,
            start_date=timezone.localdate(),
        )

    def invite_user(self, email: str):
        if self.user_projects.filter(user__email=email).exists():
            raise ValidationError(_('User already in project'))

        if self.invitations.filter(email=email, deleted_at__isnull=True).exists():
            raise ValidationError(_('User already invited'))

        invitation, created = Invitation.include_deleted_objects.get_or_create(
            email=email, project=self,
        )
        if not created:
            invitation.deleted_at = None
            invitation.save(update_fields=['deleted_at', 'updated_at'])
            invitation.send()

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

    def delete_user(self, user_id):
        u2p = self.user_projects.get(user_id=user_id)
        if u2p.role == UserProject.OWNER:
            raise ValidationError(_('You cannot delete an owner from his own project'))
        u2p.delete()
        emails.member_deleted(u2p.user, self)

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

    def add_subscription(self, subscription: 'Subscription', invoice=None):
        assert isinstance(subscription, Subscription)
        current_p2s = ProjectSubscription.objects.get(
            project=self,
            status=ProjectSubscription.ACTIVE,
        )
        # if subscription.is_default:
        #    raise ValidationError(_('Can\'t add default subscription'))
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
            raise ValidationError(_('Project have subscription on a grace period, can\'t add new subscription'))

        if current_p2s.subscription == subscription:
            raise ValidationError(gettext('Project already on {}').format(subscription.name))

        if current_p2s.subscription.is_default:
            current_p2s.status = ProjectSubscription.PAST
            current_p2s.save()
            new_p2s = ProjectSubscription.objects.create(
                project=self,
                subscription=subscription,
                status=ProjectSubscription.ACTIVE,
                start_date=timezone.localdate(),
                is_grace_period=True,
            )
            if invoice:
                invoice.project_subscription = new_p2s
                invoice.project_subscription.paid_up()
                invoice.start_date = new_p2s.start_date
                invoice.end_date = new_p2s.generate_expiring_date()
                invoice.save()
            else:
                Invoice.objects.create(project_subscription=new_p2s)
        else:
            if current_p2s.is_grace_period:
                raise ValidationError(_('Project have subscription on a grace period, can\'t add new subscription'))
            new_p2s = ProjectSubscription.objects.create(
                project=self,
                subscription=subscription,
                status=ProjectSubscription.FUTURE,
                start_date=current_p2s.expiring_date,
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

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')


class Subscription(DataOceanModel):
    MONTH_PERIOD = 'month'
    YEAR_PERIOD = 'year'
    PERIODS = (
        (MONTH_PERIOD, 'Month'),
        (YEAR_PERIOD, 'Year'),
    )

    name = models.CharField(_('name'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True, default='')
    price = models.PositiveIntegerField(_('price'), default=0)
    requests_limit = models.IntegerField(_('requests limit'), help_text='Limit for API requests from the project')
    platform_requests_limit = models.IntegerField(
        _('platform requests limit'),
        help_text='Limit for API requests from the project via platform',
    )
    periodicity = models.CharField(max_length=5, choices=PERIODS, default=MONTH_PERIOD, help_text='days')
    grace_period = models.SmallIntegerField(_('grace_period'), default=10, help_text='days')
    is_custom = models.BooleanField(
        _('is custom'), blank=True, default=False,
        help_text='Custom subscription not shown to users',
    )
    is_default = models.BooleanField(_('is default'), blank=True, default=False)

    pep_checks = models.BooleanField(
        blank=True, default=False,
        help_text='Allow to use api/pep/check/ endpoint',
    )
    pep_checks_per_minute = models.PositiveSmallIntegerField(default=0)
    pep_db_downloading = models.BooleanField(blank=True, default=False)
    position = models.PositiveSmallIntegerField(default=1, help_text='Position of subscription on frontend')
    yearly_subscription = models.ForeignKey(
        'self', models.PROTECT, blank=True, null=True, default=None,
        help_text='Related yearly subscription. Example: Business -> Business +',
    )

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
        ordering = ['position', 'price']
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')


class Invoice(DataOceanModel):
    paid_at = models.DateField(
        _('paid at'),
        null=True, blank=True,
        help_text='This operation is irreversible, you cannot '
                  'cancel the payment of the subscription for the project.'
    )
    payment_registration_date = models.DateField('payment registration date', auto_now_add=True)

    token = models.UUIDField(db_index=True, default=uuid.uuid4, blank=True)

    project_subscription = models.ForeignKey(
        'ProjectSubscription', on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name=_('project`s subscription'),
    )
    grace_period_block = models.BooleanField(
        _('is grace period blocked'),
        blank=True, default=True,
        help_text='If set to False, then the user will be allowed '
                  'to use "grace period" again'
    )
    note = models.TextField(blank=True, default='')

    # information about payment
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    requests_limit = models.IntegerField(_('requests limit'))
    subscription_name = models.CharField(_("subscription`s name"), max_length=200)
    project_name = models.CharField(_("project`s name"), max_length=100)
    is_custom_subscription = models.BooleanField(_("is subscription custom"), )
    price = models.IntegerField(_("price"))

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
        if self.is_overdue:
            return self.start_date + timezone.timedelta(days=settings.OVERDUE_INVOICE_DATE_INCREASE)
        return self.start_date + timezone.timedelta(days=self.project_subscription.grace_period)

    @property
    def is_overdue(self):
        return self.project_subscription.status == ProjectSubscription.PAST and self.project_subscription.is_grace_period

    def save(self, *args, **kwargs):
        p2s = self.project_subscription
        if getattr(self, 'id', False):
            invoice_old = Invoice.objects.get(pk=self.pk)
            if p2s.is_grace_period and not invoice_old.is_paid and self.is_paid:
                if self.is_overdue:
                    self.grace_period_block = False
                    #self.project_subscription.is_grace_period = False
                    super().save(update_fields=['grace_period_block'])
                    p2s.project.add_subscription(subscription=p2s.subscription, invoice=self)
                    emails.payment_confirmed(self.project_subscription)
                else:
                    p2s.paid_up()
                    self.grace_period_block = False
                    emails.payment_confirmed(p2s)
                self.payment_registration_date = timezone.localdate()
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
            self.end_date = p2s.generate_expiring_date()
            self.requests_limit = p2s.subscription.requests_limit
            self.subscription_name = p2s.subscription.name
            self.project_name = p2s.project.name
            self.price = p2s.subscription.price
            self.is_custom_subscription = p2s.subscription.is_custom
            super().save(*args, **kwargs)
            emails.new_invoice(self, p2s.project)

    def get_pdf(self, user=None) -> io.BytesIO:
        if user is None:
            user = self.project_subscription.project.owner

        current_date = timezone.localdate()
        if self.is_overdue:
            self.start_date = current_date

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
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')


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

    start_day = models.SmallIntegerField()
    start_date = models.DateField()
    expiring_date = models.DateField()
    is_grace_period = models.BooleanField(blank=True, default=True)

    requests_left = models.IntegerField()
    requests_used = models.IntegerField(blank=True, default=0)

    platform_requests_left = models.IntegerField()
    platform_requests_used = models.IntegerField(blank=True, default=0)

    periodicity = models.CharField(max_length=5, choices=Subscription.PERIODS)
    grace_period = models.SmallIntegerField(help_text='days')

    pep_checks_count_per_minute = models.PositiveSmallIntegerField(default=0)
    pep_checks_minute = models.PositiveIntegerField(default=0)

    def generate_expiring_date(self):
        year = self.start_date.year
        month = self.start_date.month
        if self.periodicity == Subscription.MONTH_PERIOD:
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
        elif self.periodicity == Subscription.YEAR_PERIOD:
            year += 1
        else:
            raise ValueError(f'periodicity = "{self.periodicity}" not supported!')

        last_day_of_month = monthrange(year, month)[1]
        if self.start_day > last_day_of_month:
            day = last_day_of_month
        else:
            day = self.start_day
        return self.start_date.replace(year, month, day)

    def update_expiring_date(self):
        if self.subscription.is_default:
            self.expiring_date = self.generate_expiring_date()
        elif self.is_grace_period:
            self.expiring_date = self.start_date + timezone.timedelta(days=self.grace_period)
        else:
            self.expiring_date = self.generate_expiring_date()

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
        self.is_grace_period = False
        self.update_expiring_date()
        self.save()

    def reset(self):
        self.is_grace_period = True
        self.requests_left = self.subscription.requests_limit
        self.requests_used = 0
        self.platform_requests_left = self.subscription.platform_requests_limit
        self.platform_requests_used = 0
        self.periodicity = self.subscription.periodicity
        self.grace_period = self.subscription.grace_period
        self.start_date = self.expiring_date
        self.update_expiring_date()

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
            # if create
            self.requests_left = self.subscription.requests_limit
            self.platform_requests_left = self.subscription.platform_requests_limit
            self.start_day = self.start_date.day
            self.periodicity = self.subscription.periodicity
            self.grace_period = self.subscription.grace_period
            self.update_expiring_date()
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
    email = models.EmailField(_('email'))
    project = models.ForeignKey('Project', models.CASCADE, related_name='invitations',
                                verbose_name=_('project'))

    # who_invited = models.ForeignKey('users.DataOceanUser', models.CASCADE,
    #                                 related_name='who_invitations')

    def send(self):
        if not self.is_deleted:
            emails.new_invitation(self)

    def __str__(self):
        return f'Invite {self.email} on {self.project}'

    class Meta:
        unique_together = [['email', 'project']]
        verbose_name = _('invitation')
        verbose_name_plural = _('invitations')


class CustomSubscriptionRequest(DataOceanModel):
    first_name = models.CharField(max_length=30, validators=[
        name_symbols_validator,
        two_in_row_validator,
    ])
    last_name = models.CharField(max_length=150, validators=[
        name_symbols_validator,
        two_in_row_validator,
    ])
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, default='')
    note = models.TextField(blank=True, default='')

    user = models.ForeignKey(
        'users.DataOceanUser', on_delete=models.PROTECT,
        blank=True, default=None, null=True,
        related_name='custom_subscription_requests'
    )

    is_processed = models.BooleanField(blank=True, default=False)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.full_name} <{self.email}>'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        emails.new_custom_sub_request(self)

    class Meta:
        ordering = ['is_processed', '-created_at']
        verbose_name = _('custom subscription request')
        verbose_name_plural = _('custom subscription requests')


class InvoiceReport(models.Model):
    created_at = models.DateField(auto_now_add=True)
    should_complete_count = models.SmallIntegerField(default=0)
    was_complete_count = models.SmallIntegerField(default=0)
    was_overdue_count = models.SmallIntegerField(default=0)
    was_overdue_grace_period_count = models.SmallIntegerField(default=0)

    @classmethod
    def create_daily_report(cls):

        invoices = {
            'should_complete': [],
            'was_complete': [],
            'was_overdue': [],
            'was_overdue_grace_period': [],
        }

        for invoice in Invoice.objects.all():
            current_date = timezone.localdate()
            if invoice.paid_at is None:
                if invoice.start_date == current_date:
                    invoices['should_complete'].append(invoice)
                elif invoice.start_date == current_date - timezone.timedelta(days=2):
                    invoices['was_overdue'].append(invoice)
                elif current_date == invoice.grace_period_end_date:
                    invoices['was_overdue_grace_period'].append(invoice)
            elif invoice.payment_registration_date == current_date - timezone.timedelta(days=1):
                invoices['was_complete'].append(invoice)

        cls.objects.create(
            should_complete_count=len(invoices['should_complete']),
            was_complete_count=len(invoices['was_complete']),
            was_overdue_count=len(invoices['was_overdue']),
            was_overdue_grace_period_count=len(invoices['was_overdue_grace_period']),
        )

        emails.create_report(invoices)

