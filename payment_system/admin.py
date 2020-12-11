from django.contrib import admin
from .models import Subscription, Invoice, ProjectSubscription
from rangefilter.filter import DateRangeFilter


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
        'get_project',
        'get_subscription',
        # 'is_paid',
        'get_expiring_date',
        'paid_at',
        'disable_grace_period_block',
        'note',
    )
    list_filter = (
        'project_subscription__subscription',
        ('paid_at', DateRangeFilter),
        ('project_subscription__expiring_date', DateRangeFilter),
        'disable_grace_period_block',
    )
    search_fields = (
        'project_subscription__project__owner__email',
        'project_subscription__project__owner__first_name',
        'project_subscription__project__owner__last_name',
        'project_subscription__project__name',
    )
    exclude = ('deleted_at',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = {'project_subscription'}
        if obj:
            if obj.is_paid or obj.disable_grace_period_block:
                readonly_fields.add('paid_at')
                readonly_fields.add('disable_grace_period_block')
            if obj.project_subscription.status == ProjectSubscription.PAST:
                readonly_fields.add('paid_at')
        return list(readonly_fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
