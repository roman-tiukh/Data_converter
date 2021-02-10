from django.db.models import Q
from django_filters import rest_framework as filters
from business_register.models.company_models import Company
from business_register.models.fop_models import Fop
from business_register.models.pep_models import Pep

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
        fields = ()


class PepFilterSet(filters.FilterSet):
    fullname = filters.CharFilter(lookup_expr='icontains')
    fullname_transcriptions_eng = filters.CharFilter(lookup_expr='icontains')
    updated_at = filters.DateFromToRangeFilter()

    name_search = filters.CharFilter(label='пошук по імені', method='filter_name_search')

    o = filters.OrderingFilter(
        fields=(
            ('fullname', 'fullname'),
            ('is_pep', 'is_pep'),
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

    class Meta:
        model = Pep
        fields = {
            'is_pep': ['exact'],
            'is_dead': ['exact'],
        }


class HistoricalCompanyRelatedFilterSet(filters.FilterSet):
    history_date = filters.DateFromToRangeFilter()
