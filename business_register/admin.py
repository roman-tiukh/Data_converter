from django.contrib import admin
from business_register.models.pep_models import Pep
from business_register.models.company_models import Company
from business_register.models.fop_models import Fop
from business_register.models.kved_models import Kved
from data_ocean.admin import RegisterModelAdmin


@admin.register(Pep)
class PepAdmin(RegisterModelAdmin):
    list_display = (
        'fullname',
        'pep_type'
    )
    search_fields = ('fullname',)
    ordering = ('updated_at',)
    list_filter = ('is_pep', 'pep_type', 'is_dead')

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Company)
class CompanyAdmin(RegisterModelAdmin):
    list_display = (
        'name',
        'edrpou',
        'country'
    )
    search_fields = ('name', 'edrpou')
    ordering = ('updated_at',)
    list_filter = ('company_type', 'country', 'source', 'status')

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Fop)
class FopAdmin(RegisterModelAdmin):
    list_display = (
        'fullname',
        'status',
        'address'
    )

    search_fields = ('fullname',)
    ordering = ('updated_at',)
    list_filter = ('status',)


@admin.register(Kved)
class KvedAdmin(RegisterModelAdmin):
    list_display = (
        'code',
        'name'
    )
    search_fields = ('name', 'code')
    ordering = ('updated_at',)
    list_filter = ('is_valid',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
