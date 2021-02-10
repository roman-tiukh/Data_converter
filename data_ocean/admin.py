from django.contrib import admin
from data_ocean.models import Register


class RegisterModelAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.can_admin_registers
        )

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(Register)
class AdminRegister(RegisterModelAdmin):
    list_display = (
        'name',
        'total_records',
        'status'
    )

    search_fields = ('name',)
    ordering = ('id',)
    list_filter = ('status',)

