from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.forms import TextInput
from rangefilter.filter import DateRangeFilter

from business_register.models.company_models import Company
from business_register.models.fop_models import Fop
from business_register.models.kved_models import Kved
from business_register.models.pep_models import Pep
from business_register.models.sanction_models import SanctionType, PersonSanction, CompanySanction, CountrySanction
from data_ocean.admin import RegisterModelAdmin, input_filter


@admin.register(Pep)
class PepAdmin(RegisterModelAdmin):
    list_display = (
        'fullname',
        'pep_type'
    )
    search_fields = ('fullname',)
    ordering = ('updated_at',)
    list_filter = ('is_pep', 'pep_type', 'is_dead')


def get_sanction_form(model):
    class SanctionAdminForm(forms.ModelForm):
        class Meta:
            widgets = {
                'types_of_sanctions': AutocompleteSelectMultiple(
                    model._meta.get_field('types_of_sanctions').remote_field,
                    admin.site,
                    attrs={
                        'data-dropdown-auto-width': 'true',
                        'data-width': '624px',
                    }
                ),
                'passports': TextInput(
                    attrs={
                        'style': 'max-width: 610px; width: 100%;',
                        'placeholder': 'ВР135468,123456789,987654321'
                    }
                ),
            }
    return SanctionAdminForm


# lower, horisontal and autocomplete for types and countries, country&registration number in display
@admin.register(SanctionType)
class SanctionTypeAdmin(RegisterModelAdmin):
    save_as = True
    list_display = ('id', 'name', 'law')
    search_fields = ('name', 'law')
    ordering = ('created_at',)
    list_filter = (
        input_filter('id', 'id', ['id'], 'exact'),
        'law',
    )

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(CountrySanction)
class CountrySanctionAdmin(RegisterModelAdmin):
    save_as = True
    form = get_sanction_form(CountrySanction)
    list_display = ('id', 'country',)
    search_fields = (
        'country__name',
        'types_of_sanctions__name',
    )
    filter_horisontal = ('types_of_sanctions', )
    autocomplete_fields = ['types_of_sanctions',]
    ordering = ('start_date',)
    list_filter = (
        input_filter('types_of_sanctions', 'types of sanctions', ['types_of_sanctions__name']),
    )

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(PersonSanction)
class PersonSanctionAdmin(RegisterModelAdmin):
    def get_countries(self, obj: PersonSanction):
        return ', '.join(obj.countries_of_citizenship.values_list('name', flat=True))
    get_countries.short_description = 'Countries of citizenship'

    save_as = True
    form = get_sanction_form(PersonSanction)
    list_display = (
        'id',
        'full_name',
        'date_of_birth',
        'start_date',
        'end_date',
        'taxpayer_number',
        'get_countries',
    )
    filter_horizontal = ('types_of_sanctions', 'countries_of_citizenship')
    autocomplete_fields = ['pep', 'countries_of_citizenship', 'types_of_sanctions']
    search_fields = (
        'full_name',
        'full_name_original',
        'taxpayer_number',
        'address',
        'place_of_birth',
        'types_of_sanctions__name',
    )
    ordering = ('start_date',)
    list_filter = (
        input_filter('id', 'id', ['id'], 'exact'),
        input_filter('types_of_sanctions', 'types of sanctions', ['types_of_sanctions__name']),
        input_filter('countries_of_citizenship', 'countries of citizenship name', ['countries_of_citizenship__name']),
        input_filter('taxpayer_number', 'taxpayer number', ['taxpayer_number']),
        input_filter('occupation', 'occupation', ['occupation']),
        input_filter('id_card', 'id card', ['id_card']),
        ('date_of_birth', DateRangeFilter),
        ('start_date', DateRangeFilter),
        ('end_date', DateRangeFilter),
        ('reasoning_date', DateRangeFilter),
        input_filter('reasoning', 'reasoning', ['reasoning']),
        input_filter('additional_info', 'additional_info', ['additional_info']),
    )

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(CompanySanction)
class CompanySanctionAdmin(RegisterModelAdmin):
    save_as = True
    form = get_sanction_form(CompanySanction)
    list_display = (
        'id',
        'name',
        'start_date',
        'end_date',
        'registration_number',
        'taxpayer_number',
        'country_of_registration',
    )
    filter_horisontal = ('types_of_sanctions', 'country_of_registration')
    autocomplete_fields = ('company', 'country_of_registration', 'types_of_sanctions')
    search_fields = (
        'name',
        'name_original',
        'registration_number',
        'address',
        'country_of_registration__name',
        'types_of_sanctions__name',
    )
    ordering = ('start_date',)
    list_filter = (
        input_filter('id', 'id', ['id'], 'exact'),
        input_filter('name', 'name', ['name']),
        input_filter('registration_number', 'registration number', ['registration_number']),
        input_filter('taxpayer_number', 'taxpayer number', ['taxpayer_number']),
        input_filter('types_of_sanctions', 'types of sanctions', ['types_of_sanctions__name']),
        input_filter('country_of_registration', 'countries of registration name', ['country_of_registration__name']),
        ('start_date', DateRangeFilter),
        ('end_date', DateRangeFilter),
        ('reasoning_date', DateRangeFilter),
        input_filter('reasoning', 'reasoning', ['reasoning']),
        input_filter('additional_info', 'additional_info', ['additional_info']),
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
