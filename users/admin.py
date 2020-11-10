from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from payment_system.models import Subscription, Invoice, ProjectSubscription

from users.models import DataOceanUser


class DataOceanUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = DataOceanUser
        fields = ('last_name', 'first_name', 'email',)


class DataOceanUserChangeForm(UserChangeForm):
    class Meta:
        model = DataOceanUser
        fields = ('last_name', 'first_name', 'email',)


@admin.register(DataOceanUser)
class DataOceanUserAdmin(UserAdmin):
    add_form = DataOceanUserCreationForm
    form = DataOceanUserChangeForm
    list_display = ('last_name', 'first_name', 'email', 'is_staff', 'is_active',)
    list_filter = ('last_name', 'first_name', 'email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('last_name', 'first_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


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
