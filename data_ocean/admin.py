from django.contrib import admin
from django.db.models import Q

from data_ocean.models import Register


class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return (),

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


def input_filter(parameter: str, label: str, fields: list or tuple, lookup: str = 'icontains'):
    class CustomInputFilter(InputFilter):
        parameter_name = parameter
        title = label

        def queryset(self, request, queryset):
            if self.value():
                query_filter = None
                for field in fields:
                    if query_filter is None:
                        query_filter = Q(**{f'{field}__{lookup}': self.value()})
                    else:
                        query_filter = query_filter | Q(**{f'{field}__{lookup}': self.value()})
                return queryset.filter(query_filter)
    return CustomInputFilter


class RegisterModelAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.datasets_admin
        )

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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

