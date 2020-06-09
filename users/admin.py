from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from users.models import DataOceanUser


class DataOceanUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = DataOceanUser
        fields = ('email',)


class DataOceanUserChangeForm(UserChangeForm):
    class Meta:
        model = DataOceanUser
        fields = ('email',)


class DataOceanUserAdmin(UserAdmin):
    add_form = DataOceanUserCreationForm
    form = DataOceanUserChangeForm
    model = DataOceanUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
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


admin.site.register(DataOceanUser, DataOceanUserAdmin)
