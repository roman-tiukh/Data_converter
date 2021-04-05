from django.contrib import admin

from business_register.models.company_models import Company
from business_register.models.fop_models import Fop
from business_register.models.kved_models import Kved
from business_register.models.pep_models import Pep
from business_register.models.sanction_models import SanctionType, Sanction
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


@admin.register(SanctionType)
class SanctionTypeAdmin(RegisterModelAdmin):
    list_display = ('name', 'law')
    search_fields = ('name', 'law')
    ordering = ('created_at',)
    list_filter = ('law',)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(Sanction)
class SanctionAdmin(RegisterModelAdmin):
    list_display = (
        'object_name',
        'country',
        'taxpayer_number',
        'taxpayer_number',
        'end_date',
    )
    search_fields = (
        'name',
        'object_origin_name',
        'registration_number',
        'taxpayer_number',
        'address',
        'place_of_birth',
        'types_of_sanctions__name',
        'position',
        'country__name'
    )
    ordering = ('start_date', 'country')
    list_filter = (
        'object_type',
        'is_foreign',
        'types_of_sanctions__name',
        'country__name'
    )

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


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
