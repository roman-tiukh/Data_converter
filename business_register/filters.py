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
    fullname = filters.CharFilter(lookup_expr='iexact')
    address = filters.CharFilter(lookup_expr='icontains')

    o = filters.OrderingFilter(
        fields=(
            ('fullname', 'fullname'),
            ('status__name', 'status'),
            ('address', 'address'),
            ('registration_date', 'registration_date'),
            ('termination_date', 'termination_date'),
        ),
    )

    class Meta:
        model = Fop
        fields = {
            'status': ['exact'],
            'registration_date': ['exact', 'lt', 'gt'],
            'termination_date': ['exact', 'lt', 'gt'],
            'authority': ['exact']
        }


class KvedFilterSet(filters.FilterSet):
    code = filters.CharFilter(lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')

    o = filters.OrderingFilter(
        fields=(
            ('code', 'code'),
            ('name', 'name'),
            ('group__name', 'group'),
            ('division__name', 'division'),
            ('section__name', 'section'),
        ),
    )

    class Meta:
        model = Kved
        fields = {}


class PepFilterSet(filters.FilterSet):
    fullname = filters.CharFilter(lookup_expr='icontains')
    fullname_transcriptions_eng = filters.CharFilter(lookup_expr='icontains')
    name_search = filters.CharFilter(label=_('Options for writing full name'),
                                     method='filter_name_search')
    updated_at = filters.DateFromToRangeFilter()
    is_pep = filters.BooleanFilter(widget=ValidatedBooleanWidget)
    is_dead = filters.BooleanFilter(widget=ValidatedBooleanWidget)
    pep_type = filters.ChoiceFilter(choices=Pep.TYPES)
    related_company = filters.CharFilter(label=_("Associated company`s number (provide a number)"),
                                         method='filter_related_company')
    last_job_title = filters.CharFilter(lookup_expr='icontains')
    last_employer = filters.CharFilter(lookup_expr='icontains')

    o = filters.OrderingFilter(
        fields=(
            ('fullname', 'fullname'),
            ('fullname_and_dob', 'fullname_and_dob'),
            ('is_pep', 'is_pep'),
            ('pep_type', 'pep_type'),
            ('pep_type', 'pep_type'),
            ('last_job_title', 'last_job_title'),
            ('last_employer', 'last_employer'),
        ),
    )

    def filter_name_search(self, queryset, name, value):
        return queryset.filter(
            Q(fullname__icontains=value) |
            Q(fullname_transcriptions_eng__icontains=value)
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
