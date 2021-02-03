from django.contrib import admin
from django.contrib import messages
from django import forms
from django.utils import timezone

from .models import Subscription, Invoice, ProjectSubscription, Project
from rangefilter.filter import DateRangeFilter


def set_default_subscription(model_admin, request, queryset):
    if queryset.count() != 1:
        model_admin.message_user(request, 'Only one subscription can be default', messages.ERROR)
        return
    Subscription.objects.update(is_default=False)
    queryset.update(is_default=True)
set_default_subscription.short_description = 'Set subscription as default'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price',
        'requests_limit',
        'duration',
        'grace_period',
        'is_custom',
        'is_default',
    )
    list_filter = (
        'is_custom',
        'is_default',
        'requests_limit'
    )
    search_fields = (
        'name',
        'price'
    )
    fields = (
        'name',
        'description',
        'price',
        'requests_limit',
        'duration',
        'grace_period',
        'is_custom',
        'is_default',
    )
    readonly_fields = (
        'is_default',
    )
    actions = [set_default_subscription]
    actions_on_bottom = True

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
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

    list_display = (
        'get_owner',
        # 'get_project',
        'project_name',
        'get_subscription',
        # 'is_paid',
        'get_expiring_date',
        'paid_at',
        'grace_period_block',
        'note',
    )
    list_filter = (
        'project_subscription__subscription',
        ('paid_at', DateRangeFilter),
        ('project_subscription__expiring_date', DateRangeFilter),
        'grace_period_block',
    )
    search_fields = (
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
        }
        if obj:
            if timezone.localdate() < obj.project_subscription.expiring_date:
                readonly_fields.add('grace_period_block')
            else:
                readonly_fields.add('paid_at')
            if obj.is_paid or not obj.grace_period_block:
                readonly_fields.add('paid_at')
                readonly_fields.add('grace_period_block')
            if obj.project_subscription.status == ProjectSubscription.PAST:
                readonly_fields.add('paid_at')
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
class ProjectAdmin(admin.ModelAdmin):
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
        # ('disabled_at', DateRangeFilter),
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
