from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, Group
from django.contrib.auth.forms import UserCreationForm
from rest_framework.authtoken.models import Token

from payment_system.models import Project
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


class ProjectsInline(admin.TabularInline):
    def active_subscription(self, obj: Project):
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
        'active_subscription',
        'requests_left',
        'requests_used',
        'platform_requests_left',
        'platform_requests_used',
        'expiring_date',
        'is_grace_period',
    )
    readonly_fields = fields
    model = Project

    def has_add_permission(self, request, obj):
        return False


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
            'can_admin_registers',
            'can_view_users',
            'can_admin_payment_system',
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

    def get_inlines(self, request, obj):
        inlines = self.inlines.copy()
        if request.user.can_admin_payment_system:
            inlines.append(ProjectsInline)
        return inlines

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.can_view_users

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

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
        return request.user.is_superuser or request.user.can_view_users

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.can_view_users

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
