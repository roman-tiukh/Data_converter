from django.contrib import admin
from django.contrib import messages
from django import forms
from django.utils import timezone

from data_ocean.admin import input_filter
from .models import Subscription, Invoice, ProjectSubscription, Project, CustomSubscriptionRequest, Invitation
from rangefilter.filter import DateRangeFilter


class PaymentSystemModelAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_authenticated and (
                request.user.is_superuser or request.user.payment_system_admin
        )

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


def set_default_subscription(model_admin, request, queryset):
    if queryset.count() != 1:
        model_admin.message_user(request, 'Only one subscription can be default', messages.ERROR)
        return
    Subscription.objects.update(is_default=False)
    queryset.update(is_default=True)


set_default_subscription.short_description = 'Set subscription as default'


@admin.register(Subscription)
class SubscriptionAdmin(PaymentSystemModelAdmin):
    list_display = (
        'name',
        'price',
        'requests_limit',
        'periodicity',
        'grace_period',
        'pep_checks',
        'is_custom',
        'is_default',
    )
    list_filter = (
        'periodicity',
        'is_custom',
        'is_default',
        'requests_limit',
        'pep_checks',
        'pep_db_downloading',
    )
    search_fields = (
        'name',
    )
    fields = (
        'name',
        'description',
        'price',
        'requests_limit',
        'platform_requests_limit',
        'periodicity',
        'grace_period',
        'pep_checks',
        'pep_checks_per_minute',
        'pep_db_downloading',
        'position',
        'yearly_subscription',
        'is_custom',
        'is_default',
    )
    readonly_fields = ('is_default',)
    autocomplete_fields = ('yearly_subscription',)
    actions = [set_default_subscription]
    actions_on_bottom = True

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


@admin.register(Invoice)
class InvoiceAdmin(PaymentSystemModelAdmin):
    def get_owner(self, obj: Invoice):
        return obj.project_subscription.project.owner

    get_owner.short_description = 'Owner'
    get_owner.admin_order_field = 'project_subscription__project__owner'

    def get_project(self, obj: Invoice):
        return obj.project_subscription.project

    get_project.short_description = 'Project'
    get_project.admin_order_field = 'project_subscription__project__name'

    def get_subscription(self, obj: Invoice):
        return obj.project_subscription.subscription

    get_subscription.short_description = 'Subscription'
    get_subscription.admin_order_field = 'project_subscription__subscription__name'

    def get_expiring_date(self, obj: Invoice):
        return obj.project_subscription.expiring_date

    get_expiring_date.short_description = 'Expiring date'
    get_expiring_date.admin_order_field = 'project_subscription__expiring_date'

    def get_invoice_number(self, obj: Invoice):
        return f'#{obj.id}'

    get_invoice_number.short_description = 'Invoice #'
    get_invoice_number.admin_order_field = 'id'

    def get_invoice_date(self, obj: Invoice):
        return obj.created_at.date()

    get_invoice_date.short_description = 'Invoice date'
    get_invoice_date.admin_order_field = 'created_at'

    list_display = (
        'get_invoice_number',
        'get_invoice_date',
        'get_owner',
        # 'get_project',
        'project_name',
        'get_subscription',
        # 'is_paid',
        'get_expiring_date',
        'paid_at',
        'grace_period_block',
        # 'note',
    )
    list_filter = (
        input_filter('id', 'invoice #', ['id'], 'exact'),
        input_filter('project_name', 'project name', ['project_subscription__project__name']),
        input_filter('project_owner', 'project owner (name, email)', [
            'project_subscription__project__owner__email',
            'project_subscription__project__owner__first_name',
            'project_subscription__project__owner__last_name',
        ]),
        'project_subscription__subscription',
        ('paid_at', DateRangeFilter),
        ('project_subscription__expiring_date', DateRangeFilter),
        'grace_period_block',
    )
    search_fields = (
        'id',
        'project_subscription__project__owner__email',
        'project_subscription__project__owner__first_name',
        'project_subscription__project__owner__last_name',
        'project_subscription__project__name',
    )
    exclude = ('deleted_at', 'token')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = {
            'project_subscription',
            'start_date',
            'end_date',
            'requests_limit',
            'subscription_name',
            'project_name',
            'price',
            'is_custom_subscription',
            'payment_registration_date',
        }
        if obj:
            if timezone.localdate() < obj.project_subscription.expiring_date:
                readonly_fields.add('grace_period_block')
            #else:
                #readonly_fields.add('paid_at')
            if obj.is_paid or not obj.grace_period_block:
                readonly_fields.add('paid_at')
                readonly_fields.add('grace_period_block')
            #if obj.project_subscription.status == ProjectSubscription.PAST:
                #readonly_fields.add('paid_at')
        return list(readonly_fields)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields['note'].widget.attrs['rows'] = 2
        return form

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProjectForm(forms.ModelForm):
    subscription = forms.ModelChoiceField(
        queryset=Subscription.objects.all(),
        label='Add subscription to project',
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        self.instance.add_subscription(cleaned_data['subscription'])
        return cleaned_data

    class Meta:
        model = Project
        fields = ('subscription',)


@admin.register(Project)
class ProjectAdmin(PaymentSystemModelAdmin):
    def get_expiring_date(self, obj: Project):
        return obj.active_p2s.expiring_date

    get_expiring_date.short_description = 'Expiring date'

    def get_is_paid(self, obj: Project):
        return obj.active_p2s.is_paid

    get_is_paid.short_description = 'Is paid'

    list_display = (
        'id',
        'name',
        'owner',
        'disabled_at',
        'active_subscription',
        'get_expiring_date',
        'get_is_paid',
    )
    list_display_links = ('name',)
    list_filter = (
        'disabled_at',
        input_filter('owner', 'owner (name, email)', [
            'owner__email',
            'owner__first_name',
            'owner__last_name',
        ]),
        input_filter('name', 'name', ['name']),
    )
    search_fields = (
        'owner__email',
        'owner__first_name',
        'owner__last_name',
        'name',
    )
    readonly_fields = (
        'id',
        'name',
        'owner',
        'description',
        'disabled_at',
        'active_subscription',
        'get_expiring_date',
        'get_is_paid',
    )
    form = ProjectForm

    def save_model(self, request, obj, form, change):
        return obj

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(CustomSubscriptionRequest)
class CustomSubscriptionRequestAdmin(PaymentSystemModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'phone',
        'created_at',
        'is_processed',
    )
    list_display_links = ('first_name', 'last_name')
    readonly_fields = (
        'id',
        'first_name',
        'last_name',
        'email',
        'phone',
        'note',
        'user',
    )
    search_fields = (
        'id',
        'first_name',
        'last_name',
        'email',
        'phone',
    )
    list_filter = (
        'is_processed',
        ('created_at', DateRangeFilter)
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(Invitation)
class InvitationAdmin(PaymentSystemModelAdmin):
    change_form_template = 'admin/change_invitation_form.html'

    list_display = (
        'id',
        'email',
        'project',
        'deleted_at',
    )
    autocomplete_fields = ('project',)
    list_filter = (
        input_filter('email', 'Email', ['email']),
        input_filter('project_name', 'project name', ['project__name']),
        input_filter('project_owner', 'project owner (name or email)', [
            'project__owner__first_name',
            'project__owner__last_name',
            'project__owner__email',
        ]),
    )
    search_fields = ('email', 'project__name')

    def response_change(self, request, obj: Invitation):
        res = super().response_change(request, obj)
        if 'save-send-email' in request.POST:
            obj.send()
            self.message_user(request, "Email was sent")
        return res

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj:
            readonly_fields += [
                'project',
                'created_at',
                'deleted_at',
            ]
        return readonly_fields

    def get_queryset(self, request):
        return Invitation.include_deleted_objects.order_by('-deleted_at')

    def delete_model(self, request, obj):
        obj.soft_delete()
