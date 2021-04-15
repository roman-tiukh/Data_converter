from django.contrib import admin

from business_register.models.company_models import Company
from business_register.models.fop_models import Fop
from business_register.models.kved_models import Kved
from business_register.models.pep_models import Pep
from business_register.models.sanction_models import SanctionType, PersonSanction, CompanySanction, CountrySanction
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

# lower, horisontal and autocomplete for types and countries, country&registration number in display
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


@admin.register(CountrySanction)
class CountrySanctionAdmin(RegisterModelAdmin):
    list_display = ('country',)
    search_fields = (
        'country__name',
        'types_of_sanctions__name',
    )
    filter_horisontal = ('types_of_sanctions', )
    autocomplete_fields = ['types_of_sanctions',]
    ordering = ('start_date',)
    list_filter = ('types_of_sanctions__name',)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(PersonSanction)
class PersonSanctionAdmin(RegisterModelAdmin):
    list_display = (
        'full_name',
        'taxpayer_number',
        'end_date',
    )
    filter_horizontal = ('types_of_sanctions', 'countries_of_citizenship')
    autocomplete_fields = ['pep', 'countries_of_citizenship', 'types_of_sanctions']
    search_fields = (
        'full_name',
        'full_name_original_transcription',
        'taxpayer_number',
        'address',
        'place_of_birth',
        'types_of_sanctions__name',
        'position',
    )
    ordering = ('start_date', 'countries_of_citizenship')
    list_filter = (
        'is_foreign',
        'types_of_sanctions__name',
        'countries_of_citizenship__name',
    )

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(CompanySanction)
class CompanySanctionAdmin(RegisterModelAdmin):
    list_display = (
        'name',
        'country_of_registration',
        'registration_number',
        'end_date',
    )
    filter_horisontal = ('types_of_sanctions', 'country_of_registration')
    autocomplete_fields = ('company', 'country_of_registration', 'types_of_sanctions')
    search_fields = (
        'name',
        'name_original_transcription',
        'number',
        'address',
        'country_of_registration',
        'types_of_sanctions__name',
    )
    ordering = ('start_date', 'country_of_registration')
    list_filter = (
        'is_foreign',
        'types_of_sanctions__name',
        'country_of_registration__name',
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
