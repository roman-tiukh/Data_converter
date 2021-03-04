from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django_filters import rest_framework as filters

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
        ),
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
        field_name='status_name',
        lookup_expr='exact',
        help_text='Search by ФОП status. Request may contain status name. '
                  # Commented until figure out is it need or not (Litsyshyn)
                  # 'Description: 1. зареєстровано; 2. в стані припинення; 3. припинено; 4. EMP; 5. порушено справу про банкрутство;'
                  # ' 6. порушено справу про банкрутство (санація); 7. зареєстровано, свідоцтво про державну реєстрацію недійсне;'
                  # ' 8. active; 9. active - proposal to strike off; 10. liquidation; 11. administration order; '
                  # ' 12. voluntary arrangement; 13. in administration/administrative receiver; 14. in administration;'
                  # ' 15. live but receiver manager on at least one charge; 16. in administration/receiver manager;'
                  # ' 17. receivership; 18. receiver manager / administrative receiver; 19. administrative receiver;'
                  # ' 20. voluntary arrangement / administrative receiver; 21. voluntary arrangement / receiver manager;'
                  # ' 22. скасовано. '
                  '<br> Examples: зареєстровано; порушено справу про банкрутство; liquidation'
    )
    registration_date = filters.CharFilter(
        lookup_expr='exact',
        help_text='Search by date of registration in format yyyy-mm-dd.'
                  'Searching request may contain only year, year and month(separated with dash) or full date.'
                  '<br> Examples:2020; 2014-08; 1991-08-24'
    )
    registration_date__lt = filters.CharFilter(
        lookup_expr='lt',
        help_text='Find all ФОП registered before searching date. Request must be entered in format yyyy-mm-dd.'
                  'Searching request may contain only year, year and month(separated with dash) or full date.'
                  ' <br> Examples: 2010; 2007-01; 2021-03-02'
    )
    registration_date__gt = filters.CharFilter(
        lookup_expr='gt',
        help_text='Find all ФОП registered after searching date. Request must be entered in format yyyy-mm-dd.'
                  'Searching request may contain only year, year and month(separated with dash) or full date.'
                  ' <br> Examples: 2010; 2007-01; 2021-03-02'
    )
    termination_date = filters.CharFilter(
        lookup_expr='exact',
        help_text='Search by date of termination in format yyyy-mm-dd.'
                  'Searching request may contain only year, year and month(separated with dash) or full date.'
                  '<br> Examples:2020; 2014-08; 1991-08-24'
    )
    termination_date__lt = filters.CharFilter(
        lookup_expr='lt',
        help_text='Find all ФОП terminated before searching date. Request must be entered in format yyyy-mm-dd.'
                  'Searching request may contain only year, year and month(separated with dash) or full date.'
                  '<br> Examples:2020; 2014-08; 1991-08-24'
    )
    termination_date__gt = filters.CharFilter(
        lookup_expr='gt',
        help_text='Find all ФОП terminated after searching date. Request must be entered in format yyyy-mm-dd.'
                  'Searching request may contain only year, year and month(separated with dash) or full date.'
                  '<br> Examples:2020; 2014-08; 1991-08-24'
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
        help_text='Sort by fields: code, name, group__name, division__name, section__name.'
    )

    class Meta:
        model = Kved
        fields = {}


class PepFilterSet(filters.FilterSet):
    fullname = filters.CharFilter(lookup_expr='search',
                                  help_text='Filter by full name "first name middle name last name" in Ukrainian.')
    fullname_transcriptions_eng = filters.CharFilter(lookup_expr='search',
                                                     help_text='Filter by full name in English transcription.')
    name_search = filters.CharFilter(label=_('Options for writing full name'),
                                     method='filter_name_search',
                                     help_text='Search by name in fields fullname and fullname_transcriptions_eng.')
    updated_at = filters.DateFromToRangeFilter(
        help_text='You can use the "updated_at" key to select objects with a specified modification date. '
                  'Also, you can use key "updated_at_before" to select objects before the specified date and '
                  '"updated_at_after" key to select objects after the specified date. Date must be in YYYY-MM-DD format.')
    is_pep = filters.BooleanFilter(widget=ValidatedBooleanWidget,
                                   help_text='Boolean type. Can be true or false. True - person is politically exposed person,'
                                             ' false - person is not politically exposed person.')
    is_dead = filters.BooleanFilter(widget=ValidatedBooleanWidget,
                                    help_text='Boolean type. Can be true or false. True - person is dead, false - person is alive.')
    pep_type = filters.ChoiceFilter(choices=Pep.TYPES, help_text='Filter by type of pep. Can be national politically exposed '
                                               'person, foreign politically exposed person,  politically exposed person,'
                                               ' having political functions in international organization, associated '
                                               'person or family member.')
    related_company = filters.CharFilter(label=_("Associated company`s number (provide a number)"),
                                         method='filter_related_company', help_text='Filter by related company.')
    last_job_title = filters.CharFilter(lookup_expr='icontains', help_text='Filter by title of the last job in Ukrainian.')
    last_employer = filters.CharFilter(lookup_expr='icontains', help_text='Filter by last employer in Ukrainian.')

    date_of_birth = filters.CharFilter(lookup_expr='icontains',
                                       help_text='Filter by date_of_birth, string contains type. '
                                                 'Examples: date_of_birth=1964, date_of_birth=1964-02, '
                                                 'date_of_birth=1964-02-06')

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


class HistoricalCompanyRelatedFilterSet(filters.FilterSet):
    history_date = filters.DateFromToRangeFilter()
