from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django_filters import rest_framework as filters

from business_register.forms import PepExportForm, PepCheckFilterForm
from business_register.models.company_models import Company
from business_register.models.fop_models import Fop
from business_register.models.pep_models import Pep, CompanyLinkWithPep
from data_ocean.filters import ValidatedBooleanWidget
from .models.kved_models import Kved


class CompanyFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')

    o = filters.OrderingFilter(
        fields=(
            ('edrpou', 'edrpou'),
            ('name', 'name'),
            ('status__name', 'status'),
            ('address', 'address'),
            ('authorized_capital', 'authorized_capital'),
        ), help_text='Sort by fields: edrpou, name, status, address, authorized_capital.'
    )

    class Meta:
        model = Company
        fields = {
            'edrpou': ['exact'],
        }


class FopFilterSet(filters.FilterSet):
    fullname = filters.CharFilter(
        lookup_expr='icontains',
        help_text='Search by full name "first name middle name last name" in Ukrainian. '
                  '<br> Example: багач оксана анатоліївна'
    )
    address = filters.CharFilter(
        lookup_expr='icontains',
        help_text='Search by any part of registration address or full registration address in Ukrainian. '
                  'Searching field may contain, together or separately, ZIP Code(19500), street(вул або вулиця Шевченка), '
                  'type of settlement (місто Київ, село Литвинівка), '
                  'district(Тальнівський район), region(Сумська область). Few of searching arguments must be separated with coma ( , ). '
                  'Searching request may contain uppercase and lowercase letters, numbers and punctuation.'
                  '<br>Examples: М.ГОРОДИЩЕ, ГОРОДИЩЕНСЬКИЙ РАЙОН; 19200, Черкаська область, Жашківський район, '
                  ' місто Жашків, ВУЛИЦЯ ПЕРЕМОГИ;'
    )
    #status search changed from id to name (Tiukh + Litsyhyn)
    status = filters.CharFilter(
        field_name='status__name',
        lookup_expr='icontains',
        help_text='Search by ФОП status. Request may contain status name. '
                  '<br> Examples: зареєстровано; порушено справу про банкрутство; liquidation'
    )
    registration_date = filters.DateFilter(
        lookup_expr='exact',
        help_text='Search by date of registration in format yyyy-mm-dd.'
                  'Searching request may contain only year, year and month(separated with dash) or full date.'
                  '<br> Example: 1991-08-24'
    )
    registration_date__lt = filters.DateFilter(
        field_name='registration_date',
        lookup_expr='lt',
        help_text='Find all ФОП registered before searching date. Request must be entered in format yyyy-mm-dd.'
                  'Searching request may contain only full date.'
                  ' <br> Example: 2021-03-02'
    )
    registration_date__gt = filters.DateFilter(
        field_name='registration_date',
        lookup_expr='gt',
        help_text='Find all ФОП registered after searching date. Request must be entered in format yyyy-mm-dd.'
                  'Searching request may contain only full date.'
                  ' <br> Example: 2021-03-02'
    )
    termination_date = filters.DateFilter(
        lookup_expr='exact',
        help_text='Search by date of termination in format yyyy-mm-dd.'
                  'Searching request may contain only year, year and month(separated with dash) or full date.'
                  '<br> Example: 1991-08-24'
    )
    termination_date__lt = filters.DateFilter(
        field_name='termination_date',
        lookup_expr='lt',
        help_text='Find all ФОП terminated before searching date. Request must be entered in format yyyy-mm-dd.'
                  'Searching request may contain only full date.'
                  '<br> Example: 2021-03-02'
    )
    termination_date__gt = filters.DateFilter(
        field_name='termination_date',
        lookup_expr='gt',
        help_text='Find all ФОП terminated after searching date. Request must be entered in format yyyy-mm-dd.'
                  'Searching request may contain only full date.'
                  '<br> Example: 2021-03-02'
    )
    #authority search changer from id to name (Tiukh + Litsyshyn)
    authority = filters.CharFilter(
        field_name='authority__name',
        lookup_expr='icontains',
        help_text='Search by authorized state agency which register ФОП.'
                  'Searching request may contain full state agency name or part of it in Ukrainian.'
                  '<br> Example: управління з питань державної реєстрації черкаської міської ради'
    )

    o = filters.OrderingFilter(
        fields=(
            ('fullname', 'fullname'),
            ('status__name', 'status'),
            ('address', 'address'),
            ('registration_date', 'registration_date'),
            ('termination_date', 'termination_date'),
        ),
        help_text='Arranges the results obtained for another query according to one of the following filters: fullname, '
                  'status, address, registration date, termination_date. The query must match the filter format.'
    )

    class Meta:
        model = Fop
        fields = {}


class KvedFilterSet(filters.FilterSet):
    code = filters.CharFilter(lookup_expr='icontains', help_text='Filter by code of the type of economic activity.')
    name = filters.CharFilter(lookup_expr='icontains', help_text='Filter by name of the type of economic activity.')

    o = filters.OrderingFilter(
        fields=(
            ('code', 'code'),
            ('name', 'name'),
            ('group__name', 'group'),
            ('division__name', 'division'),
            ('section__name', 'section'),
        ),
        help_text='Sort by fields: code, name, group, division, section.'
    )

    class Meta:
        model = Kved
        fields = {}


class PepFilterSet(filters.FilterSet):
    fullname = filters.CharFilter(
        lookup_expr='search',
        help_text='Filter by full name "last name first name middle name" in Ukrainian.',
    )
    fullname_transcriptions_eng = filters.CharFilter(
        lookup_expr='search',
        help_text='Filter by full name in English transcription.',
    )
    name_search = filters.CharFilter(
        label=_('Options for writing full name'),
        method='filter_name_search',
        help_text='Search by name in fields fullname and fullname_transcriptions_eng.',
    )
    updated_at = filters.DateFromToRangeFilter(
        help_text='You can use key "updated_at_before" to select objects before the specified date and '
                  '"updated_at_after" key to select objects after the specified date. '
                  'Date must be in YYYY-MM-DD format.',
    )
    updated_at_date = filters.DateFilter(
        field_name='updated_at',
        lookup_expr='date',
        help_text='You can filter updates for a specific date, '
                  'such as February 25, 2020 - updated_at_date = 2020-02-25',
    )
    is_pep = filters.BooleanFilter(
        widget=ValidatedBooleanWidget,
        help_text='Boolean type. Can be true or false. True - person is politically exposed person,'
                  ' false - person is not politically exposed person.',
    )
    is_dead = filters.BooleanFilter(
        widget=ValidatedBooleanWidget,
        help_text='Boolean type. Can be true or false. True - person is dead, false - person is alive.',
    )
    pep_type = filters.ChoiceFilter(
        choices=Pep.TYPES,
        help_text='Filter by type of pep. Can be national politically exposed  person '
                  '(pep_type=national PEP), foreign politically exposed person (pep_type='
                  'foreign PEP), having political functions in international organization '
                  '(pep_type=PEP with political functions in international organization), '
                  'associated person (pep_type=associated person with PEP), family member '
                  '(pep_type=member of PEP`s family).',
    )
    related_company = filters.CharFilter(
        label=_("Associated company`s number (provide a number)"),
        method='filter_related_company',
        help_text='Filter by related company (provide EDRPOU number).',
    )
    last_job_title = filters.CharFilter(
        lookup_expr='icontains',
        help_text='Filter by title of the last job in Ukrainian.',
    )
    last_employer = filters.CharFilter(
        lookup_expr='icontains',
        help_text='Filter by last employer in Ukrainian.',
    )

    date_of_birth = filters.CharFilter(
        lookup_expr='icontains',
        help_text='Filter by date_of_birth, string contains type. '
                  'Examples: date_of_birth=1964, date_of_birth=1964-02, '
                  'date_of_birth=1964-02-06',
    )

    o = filters.OrderingFilter(
        fields=(
            ('fullname', 'fullname'),
            ('is_pep', 'is_pep'),
            ('pep_type', 'pep_type'),
            ('last_job_title', 'last_job_title'),
            ('last_employer', 'last_employer'),
        ),
        help_text='Sort by fields: fullname, is_pep, pep_type, last_job_title, last_employer.'
    )

    def filter_name_search(self, queryset, name, value):
        return queryset.filter(
            Q(fullname__search=value) |
            Q(fullname_transcriptions_eng__search=value)
        )

    def filter_related_company(self, queryset, value, company_number):
        peps_id = CompanyLinkWithPep.objects.filter(
            company__edrpou=company_number
        ).values_list(
            'pep_id', flat=True
        )
        return queryset.filter(id__in=peps_id)

    class Meta:
        model = Pep
        fields = {}


class PepExportFilterSet(filters.FilterSet):
    updated_at = filters.DateFromToRangeFilter()
    is_pep = filters.BooleanFilter()

    class Meta:
        model = Pep
        fields = {}
        form = PepExportForm


class PepCheckFilterSet(filters.FilterSet):
    first_name = filters.CharFilter(
        lookup_expr='iexact',
        help_text='Filter by first name of PEP in Ukrainian',
    )
    last_name = filters.CharFilter(
        lookup_expr='iexact',
        help_text='Filter by last name of PEP in Ukrainian',
    )
    middle_name = filters.CharFilter(
        lookup_expr='iexact',
        help_text='Filter by middle name of PEP in Ukrainian',
    )
    fullname_transcription = filters.CharFilter(
        field_name='fullname_transcriptions_eng',
        lookup_expr='search',
        help_text='Filter by fullname transcription, min length of value = 2 words. '
                  'Examples: ivan ivanovich, ivanov ivan ivanovich'
    )
    date_of_birth = filters.CharFilter(
        lookup_expr='contains',
        help_text='Filter by date_of_birth, string contains type. '
                  'Examples: date_of_birth=1964, date_of_birth=1964-02, '
                  'date_of_birth=1964-02-06'
    )

    class Meta:
        model = Pep
        fields = {}
        form = PepCheckFilterForm


class HistoricalCompanyRelatedFilterSet(filters.FilterSet):
    history_date = filters.DateFromToRangeFilter()
