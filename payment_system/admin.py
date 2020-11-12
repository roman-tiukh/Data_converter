from django.contrib import admin
from .models import Subscription, Invoice


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'custom',
        'name',
        'description',
        'price',
        'requests_limit',
        'duration',
        'grace_period'
    )
    list_filter = (
        'custom',
        'requests_limit'
    )
    search_fields = (
        'name',
        'price'
    )
    exclude = ('deleted_at',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'paid_at',
        'info',
        'project',
        'subscription'
    )
    list_filter = (
        'paid_at',
        'project',
        'subscription'
    )
    search_fields = ('info',)
    exclude = ('deleted_at',)
