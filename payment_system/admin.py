from django.contrib import admin
from .models import Subscription, Invoice


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
    list_display = (
        'project_subscription',
        'is_paid',
        'paid_at',
        'note',
        'disable_grace_period_block',
    )
    list_filter = (
        'paid_at',
        'disable_grace_period_block',
        'project_subscription__subscription',
    )
    search_fields = (
        'project_subscription__project__name',
        'project_subscription__subscription__name',
        'note',
    )
    exclude = ('deleted_at',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['project_subscription']
        if obj and obj.is_paid:
            readonly_fields.append('paid_at')
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
