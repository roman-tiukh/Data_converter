from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

from payment_system.models import Project, Subscription
from users.models import DataOceanUser, Question


admin.site.unregister(Group)
admin.site.unregister(Token)


class DataOceanUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = DataOceanUser
        fields = ('last_name', 'first_name', 'email',)


# class DataOceanUserChangeForm(UserChangeForm):
#     class Meta:
#         model = DataOceanUser
#         fields = ('last_name', 'first_name', 'email',)

class ProjectsInlineForm(forms.ModelForm):
    p2s = None

    subscription = forms.ModelChoiceField(
        queryset=Subscription.objects.all(),
        label='Subscription',
        required=True,
        help_text='Change the subscription will add it as future to project, if it possible.',
    )

    requests_left = forms.IntegerField(
        required=True,
        label='Requests left',
    )
    platform_requests_left = forms.IntegerField(
        required=True,
        label='Platform requests left',
    )
    expiring_date = forms.DateField(
        required=True,
        label='Expiring date',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self.instance, 'id'):
            self.p2s = self.instance.active_p2s
            if not self.p2s.is_grace_period:
                self.fields['expiring_date'].widget.attrs['readonly'] = True

    def clean_expiring_date(self):
        expiring_date = self.cleaned_data['expiring_date']
        now = timezone.localdate()
        if expiring_date > self.p2s.start_date + timezone.timedelta(days=self.p2s.duration):
            raise ValidationError(_('It cannot be longer than the duration of the tariff plan'))
        if expiring_date <= now:
            raise ValidationError(_('Must be later than the current day'))
        return expiring_date

    def clean(self):
        cleaned_data = super().clean()
        if 'subscription' in self.changed_data and self.is_valid():
            # TODO: move saving to save method
            self.instance.add_subscription(cleaned_data['subscription'])
        return cleaned_data

    def get_initial_for_field(self, field, field_name):
        if field_name == 'requests_left':
            return self.p2s.requests_left
        elif field_name == 'platform_requests_left':
            return self.p2s.platform_requests_left
        elif field_name == 'expiring_date':
            return self.p2s.expiring_date
        elif field_name == 'subscription':
            return self.p2s.subscription
        else:
            return super().get_initial_for_field(field, field_name)

    def save(self, commit=True):
        instance = super().save(commit)

        self.p2s.requests_left = self.cleaned_data['requests_left']
        self.p2s.platform_requests_left = self.cleaned_data['platform_requests_left']
        update_fields = ['requests_left', 'platform_requests_left', 'updated_at']
        if self.p2s.is_grace_period:
            self.p2s.expiring_date = self.cleaned_data['expiring_date']
            update_fields.append('expiring_date')

        self.p2s.save(update_fields=update_fields)
        return instance

    class Meta:
        model = Project
        fields = ('requests_left', 'platform_requests_left')


class ProjectsInline(admin.TabularInline):
    form = ProjectsInlineForm

    def subscription(self, obj: Project):
        return obj.active_subscription.name

    def requests_left(self, obj: Project):
        return obj.active_p2s.requests_left

    def requests_used(self, obj: Project):
        return obj.active_p2s.requests_used

    def platform_requests_left(self, obj: Project):
        return obj.active_p2s.platform_requests_left

    def platform_requests_used(self, obj: Project):
        return obj.active_p2s.platform_requests_used

    def expiring_date(self, obj: Project):
        return obj.active_p2s.expiring_date

    def is_grace_period(self, obj: Project):
        return obj.active_p2s.is_grace_period

    can_delete = False
    extra = 0
    fields = (
        'subscription',
        'requests_left',
        'requests_used',
        'platform_requests_left',
        'platform_requests_used',
        'expiring_date',
        'is_grace_period',
    )
    readonly_fields = (
        # 'subscription',
        'requests_used',
        'platform_requests_used',
        'is_grace_period',
    )
    model = Project

    def has_add_permission(self, request, obj):
        return False

    def has_module_permission(self, request):
        return request.user.is_staff and request.user.payment_system_admin

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.payment_system_admin


@admin.register(DataOceanUser)
class DataOceanUserAdmin(UserAdmin):
    add_form = DataOceanUserCreationForm
    # form = DataOceanUserChangeForm
    list_display = (
        'id',
        '__str__',
        'date_joined',
        'last_login',
        'date_of_birth',
        'organization',
        'language',
        'is_staff',
        'is_active',
    )
    list_display_links = ('__str__',)
    list_filter = (
        'date_joined',
        'last_login',
        'date_of_birth',
        'language',
        'is_staff',
        'is_active',
        'is_superuser',
    )
    fieldsets = (
        ('Main info', {'fields': (
            'id',
            'email',
            'first_name',
            'last_name',
            'date_of_birth',
            'organization',
            'position',
            'language',
        )}),
        ('Permissions', {'fields': (
            'is_staff',
            'is_active',
            'is_superuser',
            'datasets_admin',
            'users_viewer',
            'payment_system_admin',
        )}),
        ('Other', {'fields': (
            'date_joined',
            'last_login',
            'password',
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('last_name', 'first_name', 'email', 'organization')
    ordering = ('date_joined',)
    readonly_fields = [
        'id',
        'last_name',
        'first_name',
        'email',
        'date_joined',
        'last_login',
        'date_of_birth',
        'organization',
        'position',
        'language',
    ]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + [
                'is_staff',
                'is_active',
                'is_superuser',
                'datasets_admin',
                'users_viewer',
                'payment_system_admin',
                'password',
            ]
        return self.readonly_fields

    def get_inlines(self, request, obj):
        if request.user.is_superuser or request.user.payment_system_admin:
            return self.inlines + [ProjectsInline]
        return self.inlines

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.users_viewer

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.users_viewer

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'user',
        'answered',
    )
    exclude = ('deleted_at',)
    list_filter = (
        'answered',
        'created_at',
    )
    search_fields = (
        'text',
        'user__email',
        'user__first_name',
        'user__last_name',
    )
    readonly_fields = (
        'text',
        'user',
    )
    ordering = ('created_at',)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.users_viewer

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.users_viewer

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
